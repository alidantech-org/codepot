from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from tempfile import SpooledTemporaryFile, TemporaryDirectory
from zipfile import BadZipFile, ZipFile

from dryv_cli.connections.api import DryvApiClient
from dryv_cli.generation import PlannedBuild

from .manifest import planned_artifacts, verify_bundle_manifest
from .model import ArtifactSet, ReceivedArtifact
from .verify import ArtifactVerificationError, content_hash_stream, safe_artifact_path, verify_file


def receive_bundle(api: DryvApiClient, planned: PlannedBuild) -> ArtifactSet:
    planned_meta = planned_artifacts(planned.plan)
    workspace = TemporaryDirectory(prefix="dryv-artifacts-")
    root = Path(workspace.name)
    bundle = SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
    try:
        download = api.download_bundle(planned.build_id, bundle)
        size, digest = content_hash_stream(bundle)
        if size != download.size or digest != download.content_hash:
            raise ArtifactVerificationError("CLI_BUNDLE_HASH", "downloaded bundle bytes do not match dryv-api metadata")
        bundle.seek(0)
        try:
            archive = ZipFile(bundle, mode="r")
        except BadZipFile as exc:
            raise ArtifactVerificationError("CLI_BUNDLE_ZIP", "downloaded bundle is not a valid ZIP archive") from exc
        with archive:
            infos = archive.infolist()
            names = tuple(item.filename for item in infos)
            if len(names) != len(set(names)):
                raise ArtifactVerificationError("CLI_BUNDLE_DUPLICATE", "bundle ZIP contains duplicate entry names")
            if ".dryv/manifest.json" not in names:
                raise ArtifactVerificationError("CLI_BUNDLE_MANIFEST", "bundle ZIP is missing .dryv/manifest.json")
            try:
                manifest_document = json.loads(archive.read(".dryv/manifest.json").decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise ArtifactVerificationError("CLI_BUNDLE_MANIFEST", "bundle manifest is not valid UTF-8 JSON") from exc
            entries = verify_bundle_manifest(
                manifest_document,
                build_id=planned.build_id,
                plan_hash=planned.plan_hash,
                planned=planned_meta,
            )
            if download.artifact_count != len(entries):
                raise ArtifactVerificationError("CLI_BUNDLE_COUNT", "bundle artifact count does not match HTTP metadata")
            expected_names = {".dryv/manifest.json", *(_entry_path(item) for item in entries)}
            if set(names) != expected_names:
                raise ArtifactVerificationError("CLI_BUNDLE_CONTENTS", "bundle ZIP entries do not match its manifest")

            artifacts: list[ReceivedArtifact] = []
            for entry in entries:
                artifact_id = _entry_string(entry, "artifactId")
                path = _entry_path(entry)
                safe_artifact_path(path)
                expected_size = _entry_int(entry, "size")
                expected_hash = _entry_string(entry, "contentHash")
                content_path = root / sha256(artifact_id.encode("utf-8")).hexdigest()
                with archive.open(path, mode="r") as source, content_path.open("wb") as target:
                    while True:
                        chunk = source.read(64 * 1024)
                        if not chunk:
                            break
                        target.write(chunk)
                verify_file(content_path, size=expected_size, content_hash=expected_hash, artifact_id=artifact_id)
                metadata = planned_meta[artifact_id]
                artifacts.append(
                    ReceivedArtifact(
                        artifact_id,
                        path,
                        expected_size,
                        expected_hash,
                        content_path,
                        metadata.provenance,
                    )
                )
        return ArtifactSet(
            planned.build_id,
            planned.plan_hash,
            tuple(sorted(artifacts, key=lambda item: item.provenance.plan_index)),
            workspace,
        )
    except Exception:
        workspace.cleanup()
        raise
    finally:
        bundle.close()


def _entry_path(value: dict[str, object]) -> str:
    return _entry_string(value, "path")


def _entry_string(value: dict[str, object], key: str) -> str:
    item = value.get(key)
    if not isinstance(item, str) or not item:
        raise ArtifactVerificationError("CLI_BUNDLE_MANIFEST", f"bundle artifact {key} must be a non-empty string")
    return item


def _entry_int(value: dict[str, object], key: str) -> int:
    item = value.get(key)
    if not isinstance(item, int) or isinstance(item, bool) or item < 0:
        raise ArtifactVerificationError("CLI_BUNDLE_MANIFEST", f"bundle artifact {key} must be a non-negative integer")
    return item


__all__ = ["receive_bundle"]
