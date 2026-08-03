"""Output index dependency tests."""

from __future__ import annotations

from pathlib import Path

from contracts.emission import EmissionFile
from contracts.names import make_contract_name
from contracts.template import TemplateFile, TemplateGroup, TemplateItemEmit, TemplateItemKey
from emission.dependencies.output_index import build_output_index


class Item:
    name = make_contract_name("UserModel")
    emit = TemplateItemEmit(
        group=TemplateGroup.MODELS,
        item_key=TemplateItemKey.MODEL,
        key="#/components/schemas/UserModel",
        ref="#/components/schemas/UserModel",
    )


class EnumItem:
    name = make_contract_name("UserStatus")
    emit = TemplateItemEmit(
        group=TemplateGroup.ENUMS,
        item_key=TemplateItemKey.ENUM,
        key="#/components/schemas/UserStatus",
        ref="#/components/schemas/UserStatus",
    )


def test_output_index_maps_model_ref_to_file(tmp_path: Path) -> None:
    output = tmp_path / "docs" / "user_model.md"
    file = _emission_file(output, {"model": Item()})

    index = build_output_index((file,), tmp_path)

    assert index.find_ref("#/components/schemas/UserModel") is not None
    assert index.find_ref("#/components/schemas/UserModel").relative_path.as_posix() == "docs/user_model.md"


def test_output_index_maps_enum_ref_to_file(tmp_path: Path) -> None:
    output = tmp_path / "docs" / "user_status.md"
    file = _emission_file(output, {"enum": EnumItem()}, item_key=TemplateItemKey.ENUM)

    index = build_output_index((file,), tmp_path)

    assert index.find_ref("#/components/schemas/UserStatus") is not None


def test_output_index_does_not_require_primitives_to_be_emitted(tmp_path: Path) -> None:
    index = build_output_index((), tmp_path)

    assert index.find_ref("#/components/schemas/String") is None


def _emission_file(output_path: Path, context: dict, item_key: TemplateItemKey = TemplateItemKey.MODEL) -> EmissionFile:
    context["file"] = TemplateFile(
        output_path=output_path,
        relative_path=Path("docs/user_model.md"),
        name="user_model.md",
        stem="user_model",
        suffix=".md",
        item_key=item_key,
    )
    return EmissionFile(
        template_path=Path("{model}/[model.name.path.o].md.j2"),
        output_path=output_path,
        context=context,
    )
