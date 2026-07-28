import pytest

from codepotg.generation import ExpressionError, evaluate_text
from codepotg.ir import Name, SemanticId


def test_path_expressions_resolve_only_known_scalar_properties() -> None:
    context = (("schema", (("id", SemanticId("users.schema")), ("name", Name("UserProfile")))),)
    assert (
        evaluate_text(
            "models/(schema.name.kebab.original)-(schema.id.value).ts",
            context,
        )
        == "models/user-profile-users.schema.ts"
    )


def test_literal_parentheses_and_unknown_roots_are_safe() -> None:
    assert evaluate_text("docs/((draft)).md", ()) == "docs/(draft).md"
    with pytest.raises(ExpressionError, match="unknown expression root"):
        evaluate_text("(runtime.secret)", ())
