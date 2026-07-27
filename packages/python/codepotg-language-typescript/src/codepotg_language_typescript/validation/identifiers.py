from __future__ import annotations

import re
import unicodedata

from codepotg.diagnostics import DiagnosticSeverity, Diagnostics
from codepotg.ports import IdentifierRole, IdentifierValidationRequest

from ..diagnostics import diagnostic
from ..options import (
    ReservedWordPolicy,
    TypeScriptTargetOptions,
    UnicodeIdentifierPolicy,
)
from .keywords import ALL_RESTRICTED

_ASCII_IDENTIFIER = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")
_ASCII_FILE_STEM = re.compile(r"^[A-Za-z_$][A-Za-z0-9_$.-]*$")


def validate_identifier(
    request: IdentifierValidationRequest,
    options: TypeScriptTargetOptions,
) -> Diagnostics:
    value = request.value
    found = []

    if value == "":
        return Diagnostics(
            (
                diagnostic(
                    "TS_IDENTIFIER_EMPTY",
                    "TypeScript identifier candidate is empty",
                    role=request.role.value,
                ),
            )
        )

    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        found.append(
            diagnostic(
                "TS_IDENTIFIER_INVALID",
                "TypeScript identifier contains a control character",
                role=request.role.value,
                value=value,
            )
        )
    if any(character.isspace() for character in value):
        found.append(
            diagnostic(
                "TS_IDENTIFIER_INVALID",
                "TypeScript identifier contains whitespace",
                role=request.role.value,
                value=value,
            )
        )

    if any(ord(character) > 127 for character in value):
        if options.unicode_identifier_policy is UnicodeIdentifierPolicy.ASCII_ONLY:
            found.append(
                diagnostic(
                    "TS_IDENTIFIER_UNICODE_UNSUPPORTED",
                    "Non-ASCII TypeScript identifiers are disabled by policy",
                    role=request.role.value,
                    value=value,
                )
            )
        elif not _unicode_identifier(value):
            found.append(
                diagnostic(
                    "TS_IDENTIFIER_INVALID",
                    "Candidate is not valid under the supported Unicode identifier subset",
                    role=request.role.value,
                    value=value,
                )
            )
    else:
        pattern = (
            _ASCII_FILE_STEM
            if request.role is IdentifierRole.FILE_STEM
            else _ASCII_IDENTIFIER
        )
        if pattern.fullmatch(value) is None:
            found.append(
                diagnostic(
                    "TS_IDENTIFIER_INVALID",
                    "Candidate is not a valid unquoted TypeScript identifier",
                    role=request.role.value,
                    value=value,
                )
            )

    if value in ALL_RESTRICTED:
        severity = (
            DiagnosticSeverity.ERROR
            if options.reserved_word_policy is ReservedWordPolicy.ERROR
            else DiagnosticSeverity.WARNING
        )
        found.append(
            diagnostic(
                "TS_IDENTIFIER_RESERVED",
                "Candidate is reserved or contextual in the pinned TypeScript baseline",
                severity=severity,
                role=request.role.value,
                value=value,
            )
        )

    return Diagnostics.from_iterable(found)


def _unicode_identifier(value: str) -> bool:
    if not value:
        return False
    return _unicode_start(value[0]) and all(
        _unicode_continue(character) for character in value[1:]
    )


def _unicode_start(character: str) -> bool:
    return character in {"$", "_"} or unicodedata.category(character) in {
        "Lu",
        "Ll",
        "Lt",
        "Lm",
        "Lo",
        "Nl",
    }


def _unicode_continue(character: str) -> bool:
    return (
        _unicode_start(character)
        or character in {"\u200c", "\u200d"}
        or unicodedata.category(character) in {"Mn", "Mc", "Nd", "Pc"}
    )
