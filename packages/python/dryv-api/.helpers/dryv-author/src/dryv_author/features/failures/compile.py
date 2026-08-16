from dryv.ir import Failure, Name, SemanticId

from dryv_author.compiler.context import CompilerContext
from dryv_author.core import Declaration

from .model import FailureDeclaration


def compile_failure(context: CompilerContext, declaration: Declaration) -> Failure:
    source = context.payload(declaration, FailureDeclaration)
    return Failure(SemanticId(declaration.id), Name(declaration.name), source.code, context.semantic_id(source.schema) if source.schema else None, source.message, context.kernel_data(declaration))


__all__ = ["compile_failure"]
