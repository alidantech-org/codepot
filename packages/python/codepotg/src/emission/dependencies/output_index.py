"""Index planned output files by emitted template item."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from contracts.emission import EmissionFile
from contracts.names import NameSet
from contracts.template import TemplateFile, TemplateGroup, TemplateItemKey
from emission.imports.paths import to_posix_path


@dataclass(frozen=True)
class EmittedItem:
    ref: str
    key: str
    group: TemplateGroup
    item_key: TemplateItemKey
    name: NameSet | None
    symbol_name: str
    output_path: Path
    relative_path: PurePosixPath
    file: TemplateFile


@dataclass(frozen=True)
class OutputIndex:
    by_ref: Mapping[str, EmittedItem]
    by_key: Mapping[str, EmittedItem]

    def find_ref(self, ref: str) -> EmittedItem | None:
        return self.by_ref.get(ref)


def build_output_index(files: Sequence[EmissionFile], output_root: Path) -> OutputIndex:
    by_ref: dict[str, EmittedItem] = {}
    by_key: dict[str, EmittedItem] = {}

    for file in files:
        item = _item_from_file(file, output_root)
        if item is None:
            continue
        by_key[item.key] = item
        if item.ref and _prefer_item(item, by_ref.get(item.ref)):
            by_ref[item.ref] = item

    return OutputIndex(by_ref=by_ref, by_key=by_key)


def _prefer_item(candidate: EmittedItem, current: EmittedItem | None) -> bool:
    if current is None:
        return True

    candidate_main = "." not in candidate.relative_path.stem
    current_main = "." not in current.relative_path.stem
    return candidate_main and not current_main


def _item_from_file(file: EmissionFile, output_root: Path) -> EmittedItem | None:
    template_file = file.context.get("file")
    item = file.context.get(str(template_file.item_key)) if template_file else None
    emit = getattr(item, "emit", None)
    if template_file is None or emit is None:
        return None

    relative = to_posix_path(file.output_path.relative_to(output_root))
    return EmittedItem(
        ref=emit.ref or "",
        key=emit.key,
        group=emit.group,
        item_key=emit.item_key,
        name=getattr(item, "name", None),
        symbol_name=getattr(getattr(item, "lang", None), "symbol_name", "-"),
        output_path=file.output_path,
        relative_path=relative,
        file=template_file,
    )
