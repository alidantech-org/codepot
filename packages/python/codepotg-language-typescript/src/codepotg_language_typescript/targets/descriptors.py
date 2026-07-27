from codepotg.ports import TargetDescriptor
from codepotg.versions import BehaviorVersion

TYPESCRIPT_CAPABILITIES = tuple(
    sorted(
        {
            "file.declaration_name",
            "file.extension.cts",
            "file.extension.d.cts",
            "file.extension.d.mts",
            "file.extension.d.ts",
            "file.extension.mts",
            "file.extension.ts",
            "file.extension.tsx",
            "identifier.reserved_words",
            "identifier.validate.enum_member",
            "identifier.validate.file_stem",
            "identifier.validate.namespace",
            "identifier.validate.parameter",
            "identifier.validate.property",
            "identifier.validate.type",
            "identifier.validate.value",
            "module.alias_path",
            "module.explicit_path",
            "module.extension_policy",
            "module.index_resolution",
            "module.package_path",
            "module.relative_path",
        }
    )
)

TARGETS = (
    TargetDescriptor(
        id="typescript",
        aliases=("ts",),
        extensions=tuple(
            sorted((".cts", ".d.cts", ".d.mts", ".d.ts", ".mts", ".ts"))
        ),
        behavior_version=BehaviorVersion(1),
        capabilities=TYPESCRIPT_CAPABILITIES,
    ),
    TargetDescriptor(
        id="typescript-jsx",
        aliases=("tsx",),
        extensions=(".tsx",),
        behavior_version=BehaviorVersion(1),
        capabilities=TYPESCRIPT_CAPABILITIES,
    ),
)
