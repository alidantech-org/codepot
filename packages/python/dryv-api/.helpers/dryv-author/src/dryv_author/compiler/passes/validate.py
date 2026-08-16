from dryv_author.compiler.context import CompilerContext
from dryv_author.validation import validate_declarations


def validate(context: CompilerContext) -> None:
    validate_declarations(context)


__all__ = ["validate"]
