from dryv.ir import Name, Presentation, PresentationChannel, PresentationEntry, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import PresentationDeclaration


def compile_presentation(context: CompilerContext, declaration: Declaration) -> Presentation:
    source = context.payload(declaration, PresentationDeclaration)
    entry_ids = {item.name: SemanticId(f"{declaration.id}/entry/{context.slug(item.name)}") for item in source.entries}
    return Presentation(SemanticId(declaration.id), Name(declaration.name), PresentationChannel(source.channel), tuple(PresentationEntry(id=entry_ids[item.name], name=Name(item.name), view=context.semantic_id(item.view), address=item.address, navigation_parent=entry_ids.get(item.navigation_parent) if item.navigation_parent else None, order=item.order, data=context.kernel_data(declaration, pointer=f"entry:{item.name}"), policies=tuple(context.semantic_id(ref) for ref in item.policies), operations=tuple(context.semantic_id(ref) for ref in item.operations), events=tuple(context.semantic_id(ref) for ref in item.events), workflows=tuple(context.semantic_id(ref) for ref in item.workflows)) for item in source.entries), context.kernel_data(declaration))


__all__ = ["compile_presentation"]
