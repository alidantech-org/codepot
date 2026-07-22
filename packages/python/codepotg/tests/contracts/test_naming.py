"""Tests for the unified naming provider."""

from __future__ import annotations

from src.contracts.names import make_contract_name
from utils.naming import build_name


def test_singular_input_keeps_original_and_builds_plural():
    name = build_name("user")

    assert name.snake.o == "user"
    assert name.snake.s == "user"
    assert name.snake.p == "users"


def test_plural_input_keeps_original_as_singular_and_plural():
    name = build_name("users")

    assert name.snake.o == "users"
    assert name.snake.s == "users"
    assert name.snake.p == "users"


def test_protected_input_is_invariant():
    name = build_name("shared")

    assert name.snake.o == "shared"
    assert name.snake.s == "shared"
    assert name.snake.p == "shared"


def test_plural_pascal_input_keeps_original():
    name = build_name("UserProfiles")

    assert name.pascal.o == "UserProfiles"
    assert name.pascal.s == "UserProfiles"
    assert name.pascal.p == "UserProfiles"


def test_path_case_is_available_for_all_forms():
    name = build_name("UserProfiles")

    assert name.path.o == "user_profiles"
    assert name.path.s == "user_profiles"
    assert name.path.p == "user_profiles"


def test_plural_and_singular_inputs_do_not_collapse():
    page = build_name("page")
    pages = build_name("pages")

    assert page.camel.s == "page"
    assert pages.camel.s == "pages"


def test_make_contract_name_uses_shared_provider() -> None:
    name = make_contract_name("UserProfile")

    assert name.pascal.original == "UserProfile"
    assert name.camel.original == "userProfile"
    assert name.snake.original == "user_profile"
    assert name.path.original == "user_profile"
