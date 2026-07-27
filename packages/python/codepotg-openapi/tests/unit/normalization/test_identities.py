from __future__ import annotations

from codepotg_openapi.normalization.identities import IdentityRegistry, stable_id


def test_stable_id_is_deterministic_and_source_scoped() -> None:
    first = stable_id(source="memory:a", category="schema", pointer="/Thing", hint="Thing")
    second = stable_id(source="memory:a", category="schema", pointer="/Thing", hint="Thing")
    other = stable_id(source="memory:b", category="schema", pointer="/Thing", hint="Thing")
    assert first == second
    assert first != other


def test_identity_registry_reports_duplicate_owner() -> None:
    semantic_id = stable_id(source="memory:a", category="schema", pointer="/Thing", hint="Thing")
    registry = IdentityRegistry()
    assert registry.register(semantic_id, "first") is None
    assert registry.register(semantic_id, "second") == "first"
