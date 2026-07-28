from .adapter import DartTargetAdapter


def create_plugin() -> DartTargetAdapter:
    return DartTargetAdapter()
