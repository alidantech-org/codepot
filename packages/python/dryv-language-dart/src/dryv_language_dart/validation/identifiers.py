from __future__ import annotations

import re
import unicodedata

from dryv.diagnostics import Diagnostics, DiagnosticSeverity
from dryv.ports import IdentifierRole, IdentifierValidationRequest

from ..diagnostics import diagnostic
from ..options import (
    DartTargetOptions,
    PrivateIdentifierPolicy,
    ReservedWordPolicy,
    UnicodeIdentifierPolicy,
)
from .keywords import (
    BUILT_IN_IDENTIFIERS,
    CONTEXT_SENSITIVE_WORDS,
    CONTEXTUAL_WORDS,
    RESERVED_WORDS,
)

_ASCII_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_RESTRICTED_BUILT_IN_ROLES = frozenset({IdentifierRole.TYPE, IdentifierRole.NAMESPACE})


def validate_identifier(
    request: IdentifierValidationRequest,
    options: DartTargetOptions,
) -> Diagnostics:
    value = request.value
    found = []
    if value == "":
        return Diagnostics(
            (
                diagnostic(
                    "DART_IDENTIFIER_EMPTY",
                    "Dart identifier candidate is empty",
                    role=request.role.value,
                ),
            )
        )
    if any(ord(character) < 32 or ord(character) == 127 for character in value) or any(
        character.isspace() for character in value
    ):
        found.append(
            diagnostic(
                "DART_IDENTIFIER_INVALID",
                "Dart identifier contains whitespace or control characters",
                role=request.role.value,
                value=value,
            )
        )
    if any(ord(character) > 127 for character in value):
        if options.unicode_identifier_policy is UnicodeIdentifierPolicy.ASCII_ONLY:
            found.append(
                diagnostic(
                    "DART_IDENTIFIER_UNICODE_UNSUPPORTED",
                    "Non-ASCII Dart identifiers are disabled by policy",
                    role=request.role.value,
                    value=value,
                )
            )
        elif not _unicode_identifier(value):
            found.append(
                diagnostic(
                    "DART_IDENTIFIER_INVALID",
                    "Candidate is not valid under the supported Unicode identifier subset",
                    role=request.role.value,
                    value=value,
                )
            )
    elif _ASCII_IDENTIFIER.fullmatch(value) is None:
        found.append(
            diagnostic(
                "DART_IDENTIFIER_INVALID",
                "Candidate is not a valid Dart identifier",
                role=request.role.value,
                value=value,
            )
        )
    if value in RESERVED_WORDS:
        severity = (
            DiagnosticSeverity.ERROR
            if options.reserved_word_policy is ReservedWordPolicy.ERROR
            else DiagnosticSeverity.WARNING
        )
        found.append(
            diagnostic(
                "DART_IDENTIFIER_RESERVED",
                "Candidate is reserved in the pinned Dart baseline",
                severity=severity,
                role=request.role.value,
                value=value,
            )
        )
    elif value in BUILT_IN_IDENTIFIERS:
        severity = (
            DiagnosticSeverity.ERROR
            if request.role in _RESTRICTED_BUILT_IN_ROLES
            else DiagnosticSeverity.WARNING
        )
        found.append(
            diagnostic(
                "DART_IDENTIFIER_CONTEXTUAL",
                "Built-in identifier is restricted for some Dart declaration roles",
                severity=severity,
                role=request.role.value,
                value=value,
            )
        )
    elif value in CONTEXT_SENSITIVE_WORDS:
        found.append(
            diagnostic(
                "DART_IDENTIFIER_CONTEXTUAL",
                "Candidate is context-sensitive in Dart",
                severity=DiagnosticSeverity.WARNING,
                role=request.role.value,
                value=value,
            )
        )
    elif value in CONTEXTUAL_WORDS:
        found.append(
            diagnostic(
                "DART_IDENTIFIER_CONTEXTUAL",
                "Candidate is a contextual Dart keyword permitted as an identifier",
                severity=DiagnosticSeverity.INFO,
                role=request.role.value,
                value=value,
            )
        )
    if value.startswith("_"):
        if options.private_identifier_policy is PrivateIdentifierPolicy.REQUIRE_PUBLIC:
            found.append(
                diagnostic(
                    "DART_IDENTIFIER_PRIVATE",
                    "Leading underscore creates a library-private Dart name",
                    role=request.role.value,
                    value=value,
                )
            )
        elif options.private_identifier_policy is PrivateIdentifierPolicy.ALLOW_WITH_FACT:
            found.append(
                diagnostic(
                    "DART_IDENTIFIER_PRIVATE",
                    "Leading underscore creates a library-private Dart name",
                    severity=DiagnosticSeverity.INFO,
                    role=request.role.value,
                    value=value,
                )
            )
    return Diagnostics.from_iterable(found)


def _unicode_identifier(value: str) -> bool:
    if not value:
        return False
    return _unicode_start(value[0]) and all(_unicode_continue(character) for character in value[1:])


def _unicode_start(character: str) -> bool:
    return character == "_" or unicodedata.category(character) in {
        "Lu",
        "Ll",
        "Lt",
        "Lm",
        "Lo",
        "Nl",
    }


def _unicode_continue(character: str) -> bool:
    return _unicode_start(character) or unicodedata.category(character) in {
        "Mn",
        "Mc",
        "Nd",
        "Pc",
    }
