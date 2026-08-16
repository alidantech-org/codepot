from __future__ import annotations

from dryv.ir import Group, Name, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration, RefKind

from .model import GroupDeclaration


def assemble_groups(context: CompilerContext) -> tuple[Group, ...]:
    declarations = context.declarations(RefKind.GROUP)
    children: dict[str | None, list[Declaration]] = {}
    for declaration in declarations:
        source = context.payload(declaration, GroupDeclaration)
        parent_id = None if source.parent is None else source.parent.declaration_id
        children.setdefault(parent_id, []).append(declaration)
    def build(declaration: Declaration) -> Group:
        source = context.payload(declaration, GroupDeclaration)
        owned = context.owned(declaration.id)
        return Group(id=SemanticId(declaration.id), name=Name(declaration.name), path=source.path, properties=context.compiled_for(owned, RefKind.PROPERTY), schemas=context.compiled_for(owned, RefKind.SCHEMA), operations=context.compiled_for(owned, RefKind.OPERATION), views=context.compiled_for(owned, RefKind.VIEW), storage_mappings=context.compiled_for(owned, RefKind.STORAGE), policies=context.compiled_for(owned, RefKind.POLICY), failures=context.compiled_for(owned, RefKind.FAILURE), events=context.compiled_for(owned, RefKind.EVENT), groups=tuple(build(item) for item in sorted(children.get(declaration.id, []), key=lambda x: x.id)), data=context.kernel_data(declaration), value_sources=context.compiled_for(owned, RefKind.VALUE_SOURCE))
    roots = sorted(children.get(None, []), key=lambda item: item.id)
    if not roots:
        raise ValueError("Author compilation requires at least one root group")
    return tuple(build(item) for item in roots)


__all__ = ["assemble_groups"]
