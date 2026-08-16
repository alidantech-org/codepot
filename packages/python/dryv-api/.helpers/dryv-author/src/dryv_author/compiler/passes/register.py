from dryv_author.compiler.context import CompilerContext


def register(context: CompilerContext) -> None:
    if not context.registry.all():
        context.error("AUTHOR_EMPTY", "Author contains no declarations")


__all__ = ["register"]
