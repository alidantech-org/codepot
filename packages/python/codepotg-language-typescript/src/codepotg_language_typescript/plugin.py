from .adapter import TypeScriptTargetAdapter


def create_plugin() -> TypeScriptTargetAdapter:
    return TypeScriptTargetAdapter()
