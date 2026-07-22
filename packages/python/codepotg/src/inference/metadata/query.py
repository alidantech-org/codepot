"""x-codegen query metadata inference."""

from __future__ import annotations

from typing import Any

from constants.codegen import FILTER, OPERATORS, QUERY, SEARCH, SELECT, SORT, X_CODEGEN
from inference.models.schemas import QueryMetadata


def infer_query_metadata(schema: dict[str, Any] | None) -> QueryMetadata:
    """Infer query metadata from x-codegen.query."""
    if not isinstance(schema, dict):
        return QueryMetadata()

    x_codegen = schema.get(X_CODEGEN)
    if not isinstance(x_codegen, dict):
        return QueryMetadata()

    query = x_codegen.get(QUERY)
    if not isinstance(query, dict):
        return QueryMetadata()

    return QueryMetadata(
        filterable=bool(query.get(FILTER)),
        operators=_operators(query.get(OPERATORS)),
        sortable=bool(query.get(SORT)),
        selectable=bool(query.get(SELECT)),
        searchable=bool(query.get(SEARCH)),
    )


def _operators(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, str):
        return (value,)

    if isinstance(value, list | tuple | set):
        return tuple(str(item) for item in value)

    return (str(value),)
