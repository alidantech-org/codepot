from .model import ApiVersion, BehaviorVersion, BehaviorVersions, Version

CORE_VERSION = Version.parse("2.0.0-alpha.1")
PUBLIC_API_VERSION = ApiVersion("codepotg.public", Version.parse("2.0.0"))
IR_API_VERSION = ApiVersion("codepotg.ir", Version.parse("2.0.0"))
PLUGIN_API_VERSION = ApiVersion("codepotg.plugin", Version.parse("1.0.0"))
DEFAULT_BEHAVIOR_VERSIONS = BehaviorVersions()

__all__ = [
    "ApiVersion",
    "BehaviorVersion",
    "BehaviorVersions",
    "CORE_VERSION",
    "DEFAULT_BEHAVIOR_VERSIONS",
    "IR_API_VERSION",
    "PLUGIN_API_VERSION",
    "PUBLIC_API_VERSION",
    "Version",
]
