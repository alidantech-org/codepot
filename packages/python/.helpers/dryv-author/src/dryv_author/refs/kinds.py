from enum import StrEnum


class RefKind(StrEnum):
    GROUP = "group"
    PROPERTY = "property"
    SCHEMA = "schema"
    FIELD = "field"
    OPERATION = "operation"
    EVENT = "event"
    POLICY = "policy"
    STORAGE = "storage"
    VIEW = "view"
    WORKFLOW = "workflow"
    WORKFLOW_STEP = "workflow_step"
    VALUE_SOURCE = "value_source"
    PRESENTATION = "presentation"
