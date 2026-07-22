"""Component index and generic component lookup.

This module provides utilities for building an index of all components
in an OpenAPI document and resolving component references.
"""

from dataclasses import dataclass
from typing import Any

from constants.openapi import COMPONENT_SECTIONS
from openapi.document import OpenApiDocument
from openapi.refs import OpenApiRef


@dataclass(frozen=True)
class ComponentKey:
    """A key identifying a component in the OpenAPI document.

    Attributes:
        section: The component section (e.g., "schemas", "responses").
        name: The component name within the section.
    """

    section: str
    name: str


@dataclass(frozen=True)
class ComponentIndex:
    """An index of all components in an OpenAPI document.

    Attributes:
        components: A mapping from (section, name) tuples to component definitions.
    """

    components: dict[tuple[str, str], dict[str, Any]]

    def has(self, ref: OpenApiRef) -> bool:
        """Check if a component reference exists in the index.

        Args:
            ref: The OpenAPI reference to check.

        Returns:
            True if the component exists, False otherwise.
        """
        key = ref.component_key
        return key is not None and key in self.components

    def get(self, ref: OpenApiRef) -> dict[str, Any] | None:
        """Get a component definition by reference.

        Args:
            ref: The OpenAPI reference to resolve.

        Returns:
            The component definition, or None if not found.
        """
        key = ref.component_key

        if key is None:
            return None

        return self.components.get(key)


def build_component_index(document: OpenApiDocument) -> ComponentIndex:
    """Build an index of all components in an OpenAPI document.

    Args:
        document: The OpenAPI document.

    Returns:
        A ComponentIndex containing all components.
    """
    components: dict[tuple[str, str], dict[str, Any]] = {}

    for section in COMPONENT_SECTIONS:
        section_value = document.components.get(section)

        if not isinstance(section_value, dict):
            continue

        for name, value in section_value.items():
            if isinstance(value, dict):
                components[(section, str(name))] = value

    return ComponentIndex(components=components)


def resolve_component_ref(
    document: OpenApiDocument, ref: OpenApiRef
) -> dict[str, Any] | None:
    """Resolve a component reference to its definition.

    Args:
        document: The OpenAPI document.
        ref: The OpenAPI reference to resolve.

    Returns:
        The component definition, or None if not found.
    """
    index = build_component_index(document)
    return index.get(ref)
