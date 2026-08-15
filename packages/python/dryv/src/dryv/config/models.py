"""Task-21 compatibility configuration exports.

Project semantics are owned by :mod:`dryv.features.project`; pack semantics are
re-exported through the local ``pack_models`` shim so this legacy module does
not coordinate sibling Features directly.
"""

from dryv.features.project import (
    ConfigScalar,
    PackInstanceConfig,
    PackSource,
    ProjectConfig,
    SourceConfig,
    freeze_object,
    freeze_value,
)

from .pack_models import BindingDefinition, OptionDefinition, PackManifest, SelectionConfig

__all__ = [
    "BindingDefinition",
    "ConfigScalar",
    "OptionDefinition",
    "PackInstanceConfig",
    "PackManifest",
    "PackSource",
    "ProjectConfig",
    "SelectionConfig",
    "SourceConfig",
    "freeze_object",
    "freeze_value",
]
