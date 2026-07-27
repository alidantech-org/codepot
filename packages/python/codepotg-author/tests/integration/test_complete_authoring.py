from __future__ import annotations

from enum import StrEnum

import pytest
from pydantic import BaseModel, Field

from codepotg_author import (
    Author,
    EventDeclaration,
    FieldOptions,
    OperationDeclaration,
    OperationOutputDeclaration,
    PolicyDeclaration,
    ProjectionStep,
    SchemaUseDeclaration,
    StorageDeclaration,
    StorageFieldDeclaration,
    ViewDeclaration,
    WorkflowDeclaration,
    WorkflowStepDeclaration,
    dumps_json,
    dumps_yaml,
    field,
    loads_json,
    loads_yaml,
)


class Status(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class Node(BaseModel):
    name: str = Field(min_length=1, max_length=40)
    status: Status
    children: list[Node] = []


Node.model_rebuild()


def test_typed_property_api_rejects_mixed_option_forms() -> None:
    author = Author("example")
    identifier = author.property(
        "identifier",
        str,
        options=FieldOptions(required=True, min_length=1),
    )
    schema = author.schema("Record", {"id": identifier, "name": field(str, max_length=80)})
    assert author.declaration(schema).name == "Record"
    with pytest.raises(ValueError, match="either options or explicit"):
        field(str, options=FieldOptions(), max_length=2)


def test_recursive_pydantic_models_compile_without_pydantic_in_ir() -> None:
    author = Author("tree")
    root = author.pydantic_model(Node)
    result = author.compile()
    assert result.ok
    assert result.contract is not None
    schema = next(
        item for item in result.contract.groups[0].schemas if item.id.value == root.declaration_id
    )
    assert {item.name.raw.original for item in schema.fields} == {"name", "status", "children"}
    assert "pydantic" not in repr(result.contract).lower()


def test_semantic_builders_compile_to_public_ir() -> None:
    author = Author("shop", version="1.0")
    group = author.group("Catalog")
    record = author.schema(
        "Record",
        {
            "id": field(str, readonly=True, min_length=1),
            "name": field(str, min_length=1, max_length=100),
        },
        group=group,
    )
    create = author.project_schema(
        record, "CreateRecord", ProjectionStep("derive_create"), group=group
    )
    changed = author.event("RecordChanged", EventDeclaration(payload_schema=record), group=group)
    operation = author.operation(
        "CreateRecord",
        OperationDeclaration(
            inputs=(SchemaUseDeclaration("body", create, required=True),),
            outputs=(OperationOutputDeclaration(record, "record"),),
            emitted_events=(changed,),
            http_method="POST",
            http_path="/records",
            operation_id="createRecord",
        ),
        group=group,
    )
    author.policy("CatalogAccess", PolicyDeclaration(roles=("admin",)), group=group)
    author.storage(
        "RecordTable",
        StorageDeclaration(
            record,
            "records",
            fields=(StorageFieldDeclaration("id", "id", unique=True),),
            primary_key=("id",),
        ),
        group=group,
    )
    author.view("RecordList", ViewDeclaration(schema=record), group=group)
    author.workflow(
        "CreateRecordFlow",
        WorkflowDeclaration(
            steps=(WorkflowStepDeclaration("create", "operation", operation=operation),),
        ),
        group=group,
    )
    result = author.compile()
    assert result.ok
    assert result.contract is not None
    compiled_group = result.contract.groups[0]
    assert len(compiled_group.operations) == 1
    assert len(compiled_group.events) == 1
    assert len(compiled_group.policies) == 1
    assert len(compiled_group.storage_mappings) == 1
    assert len(compiled_group.views) == 1
    assert len(compiled_group.workflows) == 1


def test_canonical_json_and_yaml_round_trip() -> None:
    author = Author("transport")
    author.schema("Message", {"text": field(str, min_length=1)})
    result = author.compile()
    assert result.contract is not None
    json_value = dumps_json(result.contract)
    yaml_value = dumps_yaml(result.contract)
    assert dumps_json(loads_json(json_value)) == json_value
    assert dumps_json(loads_yaml(yaml_value)) == json_value
    with pytest.raises(Exception, match="duplicate key"):
        loads_yaml("format: codepotg.ir\nformat: codepotg.ir\nversion: 1\ncontract: {}\n")


def test_non_string_enum_values_are_rejected() -> None:
    from enum import Enum

    class Bad(Enum):
        ONE = 1

    with pytest.raises(TypeError, match="must be strings"):
        Author("bad").enum_schema("Bad", Bad)
