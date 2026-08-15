"""Public feature namespace for Dryv Runtime capabilities.

Each child package is an independent capability boundary. Runtime may compose
Features through their public package roots; Features must not import Runtime
or sibling Feature internals.
"""

__all__ = [
    "artifacts",
    "authoring",
    "cache",
    "diagnostics",
    "hashing",
    "ir",
    "packs",
    "planning",
    "project",
    "resources",
    "scheduling",
    "serialization",
    "templating",
]
