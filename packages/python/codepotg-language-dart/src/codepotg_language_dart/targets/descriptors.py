from codepotg.ports import TargetDescriptor
from codepotg.versions import BehaviorVersion

DART_CAPABILITIES = tuple(
    sorted(
        {
            "file.extension.dart",
            "identifier.private_name",
            "identifier.reserved_words",
            "identifier.validate.enum_member",
            "identifier.validate.file_stem",
            "identifier.validate.namespace",
            "identifier.validate.parameter",
            "identifier.validate.property",
            "identifier.validate.type",
            "identifier.validate.value",
            "module.explicit_path",
            "module.package_path",
            "module.relative_path",
        }
    )
)

TARGETS = (
    TargetDescriptor(
        id="dart",
        aliases=(),
        extensions=(".dart",),
        behavior_version=BehaviorVersion(1),
        capabilities=DART_CAPABILITIES,
    ),
)
