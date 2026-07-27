from __future__ import annotations

import pytest

from codepotg_openapi.options import (
    ExternalReferencePolicy,
    GroupingPolicy,
    MultiTagPolicy,
    OpenApiOptions,
    OperationIdPolicy,
    OptionDecodeError,
    ValidationPolicy,
    XCodegenPolicy,
)


@pytest.mark.parametrize(
    ("key", "value", "attribute", "expected"),
    [
        ("validation", "tolerant", "validation", ValidationPolicy.TOLERANT),
        (
            "externalReferences",
            "controlled",
            "external_references",
            ExternalReferencePolicy.CONTROLLED,
        ),
        ("grouping", "tags", "grouping", GroupingPolicy.TAGS),
        (
            "multiTagPolicy",
            "explicitRequired",
            "multi_tag_policy",
            MultiTagPolicy.EXPLICIT_REQUIRED,
        ),
        (
            "operationIds",
            "require",
            "operation_ids",
            OperationIdPolicy.REQUIRE,
        ),
        ("xCodegenPolicy", "strict", "x_codegen_policy", XCodegenPolicy.STRICT),
        ("maxSourceBytes", 100, "max_source_bytes", 100),
        ("maxReferenceDepth", 4, "max_reference_depth", 4),
        ("maxDocuments", 5, "max_documents", 5),
        ("preserveUnknownExtensions", True, "preserve_unknown_extensions", True),
        ("maxPreservedDepth", 3, "max_preserved_depth", 3),
        ("maxPreservedItems", 20, "max_preserved_items", 20),
    ],
)
def test_decodes_every_option(key, value, attribute, expected) -> None:
    options = OpenApiOptions.decode(((key, value),))
    assert getattr(options, attribute) == expected


def test_defaults_are_immutable_and_canonical() -> None:
    options = OpenApiOptions.decode(())
    assert options.validation is ValidationPolicy.STRICT
    assert tuple(key for key, _ in options.canonical_items()) == tuple(
        sorted(key for key, _ in options.canonical_items())
    )
    with pytest.raises((AttributeError, TypeError)):
        options.max_documents = 1  # type: ignore[misc]


def test_unknown_option_is_rejected() -> None:
    with pytest.raises(OptionDecodeError, match="unknown option"):
        OpenApiOptions.decode((("language", "typescript"),))


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("validation", 1),
        ("validation", "fast"),
        ("maxSourceBytes", True),
        ("maxDocuments", 0),
        ("preserveUnknownExtensions", "true"),
    ],
)
def test_wrong_option_values_are_rejected(key, value) -> None:
    with pytest.raises(OptionDecodeError):
        OpenApiOptions.decode(((key, value),))


def test_options_cannot_authorize_host_or_target_behavior() -> None:
    forbidden = (
        "allowedRoot",
        "allowedHosts",
        "language",
        "framework",
        "outputPath",
        "selector",
        "facet",
    )
    for key in forbidden:
        with pytest.raises(OptionDecodeError):
            OpenApiOptions.decode(((key, "value"),))
