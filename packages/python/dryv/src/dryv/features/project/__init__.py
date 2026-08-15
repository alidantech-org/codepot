"""Meaning and validation of Dryv usage configuration (`dryv.yaml`).

The Project Feature consumes already-decoded documents and logical resource
identifiers. It performs no filesystem, Git, network, or server operations.
"""

from .decoder import ProjectConfigurationError, decode_project
from .models import BuildMode, CacheMode, ConfigScalar, PackInstanceConfig, PackSource, ProjectConfig, SourceConfig, freeze_object, freeze_value

__all__ = ["BuildMode", "CacheMode", "ConfigScalar", "PackInstanceConfig", "PackSource", "ProjectConfig", "ProjectConfigurationError", "SourceConfig", "decode_project", "freeze_object", "freeze_value"]
