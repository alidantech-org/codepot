from dryv.ir import Name, Policy, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import PolicyDeclaration


def compile_policy(context: CompilerContext, declaration: Declaration) -> Policy:
    source = context.payload(declaration, PolicyDeclaration)
    return Policy(SemanticId(declaration.id), Name(declaration.name), source.roles, source.permissions, source.scopes, source.ownership, source.conditions, context.kernel_data(declaration), context.semantic_id(source.context_schema) if source.context_schema else None, tuple(context.semantic_id(item) for item in source.policies))


__all__ = ["compile_policy"]
