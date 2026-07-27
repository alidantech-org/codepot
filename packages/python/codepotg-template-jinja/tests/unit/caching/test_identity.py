from __future__ import annotations

from codepotg_template_jinja.caching import sha256_text, stable_identity


def test_text_digest_is_stable() -> None:
    assert sha256_text("hello") == sha256_text("hello")
    assert sha256_text("hello") != sha256_text("Hello")


def test_stable_identity_is_order_sensitive_for_sequences() -> None:
    assert stable_identity(("a", "b")) != stable_identity(("b", "a"))
