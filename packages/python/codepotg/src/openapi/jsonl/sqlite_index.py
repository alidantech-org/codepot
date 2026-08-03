"""SQLite-backed indexes for lazy JSONL record discovery."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Mapping, Sequence
from pathlib import Path
from threading import RLock
from typing import Any

from .hot_index import HotIndexRegistry
from .models import RecordLocation

_DATABASE_NAME = "index.sqlite"
_FETCH_BATCH = 1_024


class SqliteIndexWriter:
    """Batch index facts into one SQLite database while JSONL stores raw records."""

    def __init__(
        self,
        root: Path,
        *,
        cache_bytes: int = 64 * 1024 * 1024,
        batch_size: int = 2_000,
    ) -> None:
        self.root = root
        self.path = root / _DATABASE_NAME
        self.batch_size = max(1, batch_size)
        self.counts = {"definitions": 0, "mentions": 0, "dependencies": 0}
        self._definitions: list[tuple[str, str, str]] = []
        self._locations: dict[str, tuple[Any, ...]] = {}
        self._mentions: list[tuple[str, str, str, str, str]] = []
        self._dependencies: list[tuple[str, str, str, str]] = []
        # The compiler constructs the writer on the producer thread, then transfers
        # exclusive use to its single record worker. Closing happens only after that
        # worker has joined, so cross-thread access is sequential rather than concurrent.
        self._connection = sqlite3.connect(self.path, check_same_thread=False)
        self._closed = False
        _configure_writer(self._connection, cache_bytes=cache_bytes)
        self._create_schema()

    def definition(
        self,
        lookup: str,
        value: str,
        location: RecordLocation,
        *,
        hot_index: HotIndexRegistry,
    ) -> None:
        self._locations[location.key] = _location_values(location)
        self._definitions.append((lookup, value, location.key))
        self.counts["definitions"] += 1
        hot_index.put_definition(lookup, value, location)
        self._flush_if_needed()

    def mention(
        self,
        index: str,
        value: str,
        *,
        item: str,
        purpose: str,
        file: str,
    ) -> None:
        self._mentions.append((index, value, item, purpose, file))
        self.counts["mentions"] += 1
        self._flush_if_needed()

    def dependency(
        self,
        *,
        source: str,
        target: str,
        purpose: str,
        file: str,
    ) -> None:
        self._dependencies.append((source, target, purpose, file))
        self.counts["dependencies"] += 1
        self._flush_if_needed()

    def close(self) -> None:
        if self._closed:
            return
        self._flush()
        self._connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS locations_section_kind
              ON locations(section, kind, key);
            CREATE INDEX IF NOT EXISTS mentions_lookup
              ON mentions(index_name, value);
            CREATE INDEX IF NOT EXISTS mentions_item
              ON mentions(item);
            CREATE INDEX IF NOT EXISTS dependencies_target
              ON dependencies(target);
            CREATE INDEX IF NOT EXISTS dependencies_source
              ON dependencies(source);
            ANALYZE;
            """
        )
        self._connection.commit()
        self._connection.close()
        self._closed = True

    def manifest(self) -> dict[str, Any]:
        return {
            category: {
                "database": _DATABASE_NAME,
                "table": category,
                "records": self.counts[category],
                "backend": "sqlite",
            }
            for category in ("definitions", "mentions", "dependencies")
        }

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE locations (
              key TEXT PRIMARY KEY,
              section TEXT NOT NULL,
              file TEXT NOT NULL,
              offset INTEGER NOT NULL,
              length INTEGER NOT NULL,
              sha256 TEXT NOT NULL,
              ref TEXT,
              kind TEXT,
              resources TEXT NOT NULL,
              pointer TEXT
            ) WITHOUT ROWID;

            CREATE TABLE definitions (
              lookup TEXT NOT NULL,
              value TEXT NOT NULL,
              location_key TEXT NOT NULL,
              PRIMARY KEY (lookup, value),
              FOREIGN KEY (location_key) REFERENCES locations(key)
            ) WITHOUT ROWID;

            CREATE TABLE mentions (
              index_name TEXT NOT NULL,
              value TEXT NOT NULL,
              item TEXT NOT NULL,
              purpose TEXT NOT NULL,
              file TEXT NOT NULL
            );

            CREATE TABLE dependencies (
              source TEXT NOT NULL,
              target TEXT NOT NULL,
              purpose TEXT NOT NULL,
              file TEXT NOT NULL
            );
            """
        )

    def _flush_if_needed(self) -> None:
        pending = len(self._definitions) + len(self._mentions) + len(self._dependencies)
        if pending >= self.batch_size:
            self._flush()

    def _flush(self) -> None:
        if self._closed or not (
            self._locations or self._definitions or self._mentions or self._dependencies
        ):
            return
        with self._connection:
            if self._locations:
                self._connection.executemany(
                    """
                    INSERT OR REPLACE INTO locations (
                      key, section, file, offset, length, sha256,
                      ref, kind, resources, pointer
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    self._locations.values(),
                )
            if self._definitions:
                self._connection.executemany(
                    """
                    INSERT OR REPLACE INTO definitions (lookup, value, location_key)
                    VALUES (?, ?, ?)
                    """,
                    self._definitions,
                )
            if self._mentions:
                self._connection.executemany(
                    """
                    INSERT INTO mentions (index_name, value, item, purpose, file)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    self._mentions,
                )
            if self._dependencies:
                self._connection.executemany(
                    """
                    INSERT INTO dependencies (source, target, purpose, file)
                    VALUES (?, ?, ?, ?)
                    """,
                    self._dependencies,
                )
        self._locations.clear()
        self._definitions.clear()
        self._mentions.clear()
        self._dependencies.clear()


class SqliteIndexReader:
    """Read-only exact and range lookup facade over one compiled cache database."""

    def __init__(self, cache_dir: Path, *, cache_bytes: int = 64 * 1024 * 1024) -> None:
        self.path = cache_dir / _DATABASE_NAME
        uri = f"{self.path.resolve().as_uri()}?mode=ro"
        self._connection = sqlite3.connect(uri, uri=True, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._lock = RLock()
        self._closed = False
        _configure_reader(self._connection, cache_bytes=cache_bytes)

    def definition(self, lookup: str, value: str) -> RecordLocation | None:
        with self._lock:
            row = self._connection.execute(
                """
                SELECT l.*
                FROM definitions AS d
                JOIN locations AS l ON l.key = d.location_key
                WHERE d.lookup = ? AND d.value = ?
                LIMIT 1
                """,
                (lookup, value),
            ).fetchone()
        return _location_from_row(row) if row is not None else None

    def locations(
        self,
        section: str,
        *,
        kinds: Sequence[str] = (),
        mention: tuple[str, str] | None = None,
    ) -> Iterator[RecordLocation]:
        """Stream locations in bounded fetch batches."""
        yield from self.iter_locations(section, kinds=kinds, mention=mention)

    def iter_locations(
        self,
        section: str,
        *,
        kinds: Sequence[str] = (),
        mention: tuple[str, str] | None = None,
    ) -> Iterator[RecordLocation]:
        clauses = ["l.section = ?"]
        parameters: list[Any] = [section]
        join = ""
        if kinds:
            placeholders = ",".join("?" for _ in kinds)
            clauses.append(f"l.kind IN ({placeholders})")
            parameters.extend(kinds)
        if mention is not None:
            join = "JOIN mentions AS m ON m.item = l.key"
            clauses.extend(("m.index_name = ?", "m.value = ?"))
            parameters.extend(mention)
        query = (
            "SELECT DISTINCT l.* FROM locations AS l "
            f"{join} WHERE {' AND '.join(clauses)} ORDER BY l.key"
        )
        with self._lock:
            cursor = self._connection.execute(query, parameters)
            while rows := cursor.fetchmany(_FETCH_BATCH):
                for row in rows:
                    yield _location_from_row(row)

    def mentions(self, index: str, value: str) -> tuple[Mapping[str, Any], ...]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT index_name, value, item, purpose, file
                FROM mentions
                WHERE index_name = ? AND value = ?
                ORDER BY item, purpose, file
                """,
                (index, value),
            ).fetchall()
        return tuple(_mention_from_row(row) for row in rows)

    def iter_mentions(self, index: str) -> Iterator[Mapping[str, Any]]:
        with self._lock:
            cursor = self._connection.execute(
                """
                SELECT index_name, value, item, purpose, file
                FROM mentions
                WHERE index_name = ?
                ORDER BY value, item, purpose, file
                """,
                (index,),
            )
            while rows := cursor.fetchmany(_FETCH_BATCH):
                for row in rows:
                    yield _mention_from_row(row)

    def dependants(self, ref: str) -> tuple[Mapping[str, Any], ...]:
        with self._lock:
            rows = self._connection.execute(
                """
                SELECT source, target, purpose, file
                FROM dependencies
                WHERE target = ?
                ORDER BY source, purpose, file
                """,
                (ref,),
            ).fetchall()
        return tuple(
            {
                "from": str(row["source"]),
                "to": str(row["target"]),
                "purpose": str(row["purpose"]),
                "file": str(row["file"]),
            }
            for row in rows
        )

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._connection.close()
            self._closed = True


def sqlite_index_path(cache_dir: str | Path) -> Path:
    return Path(cache_dir) / _DATABASE_NAME


def _configure_writer(connection: sqlite3.Connection, *, cache_bytes: int) -> None:
    cache_kib = max(2_048, cache_bytes // 1024)
    connection.executescript(
        f"""
        PRAGMA journal_mode=OFF;
        PRAGMA synchronous=OFF;
        PRAGMA locking_mode=EXCLUSIVE;
        PRAGMA temp_store=MEMORY;
        PRAGMA cache_size=-{cache_kib};
        PRAGMA foreign_keys=OFF;
        """
    )


def _configure_reader(connection: sqlite3.Connection, *, cache_bytes: int) -> None:
    cache_kib = max(2_048, cache_bytes // 1024)
    connection.executescript(
        f"""
        PRAGMA query_only=ON;
        PRAGMA temp_store=MEMORY;
        PRAGMA cache_size=-{cache_kib};
        """
    )


def _location_values(location: RecordLocation) -> tuple[Any, ...]:
    return (
        location.key,
        location.section,
        location.file,
        location.offset,
        location.length,
        location.sha256,
        location.ref,
        location.kind,
        json.dumps(location.resources, separators=(",", ":")),
        location.pointer,
    )


def _location_from_row(row: sqlite3.Row) -> RecordLocation:
    raw_resources = json.loads(str(row["resources"]))
    return RecordLocation(
        section=str(row["section"]),
        file=str(row["file"]),
        offset=int(row["offset"]),
        length=int(row["length"]),
        sha256=str(row["sha256"]),
        key=str(row["key"]),
        ref=str(row["ref"]) if row["ref"] is not None else None,
        kind=str(row["kind"]) if row["kind"] is not None else None,
        resources=tuple(str(item) for item in raw_resources),
        pointer=str(row["pointer"]) if row["pointer"] is not None else None,
    )


def _mention_from_row(row: sqlite3.Row) -> Mapping[str, Any]:
    return {
        "index": str(row["index_name"]),
        "value": str(row["value"]),
        "item": str(row["item"]),
        "purpose": str(row["purpose"]),
        "file": str(row["file"]),
    }
