from __future__ import annotations

import pytest

from dryv.diagnostics import Diagnostic, Diagnostics, DiagnosticSeverity
from dryv.features.authoring import (
    AuthorBackendHello,
    AuthorComplete,
    AuthorDiagnostic,
    AuthorDocument,
    AuthorIRRecord,
    AuthorProgress,
    AuthorRequest,
    AuthorSource,
    AuthoringError,
    AuthoringFeature,
)
from dryv.ir import Contract


class FakeSession:
    def __init__(self, messages: tuple[object, ...], *, streaming: bool = True) -> None:
        self.messages = messages
        self.streaming = streaming
        self.cancelled: list[str] = []

    def hello(self) -> AuthorBackendHello:
        return AuthorBackendHello("python-author", "1.0.0", ("python",), ("1",), (1,), self.streaming, "author:python:1")

    def author(self, request: AuthorRequest):
        return iter(self.messages)

    def cancel(self, job_id: str) -> None:
        self.cancelled.append(job_id)


def _request() -> AuthorRequest:
    return AuthorRequest(1, "job.a", "1", "python", (AuthorSource("resource://project/author.py", "text/x-python"),))


def test_record_stream_is_passed_to_canonical_decoder(connected_contract: Contract) -> None:
    seen: list[object] = []

    def decode(records):
        seen.extend(records)
        return connected_contract

    session = FakeSession((AuthorProgress("started"), AuthorIRRecord({"id": "one"}), AuthorIRRecord({"id": "two"}), AuthorDiagnostic("NOTE", "ok", "info"), AuthorComplete("job.a", "author:python:1")))
    result = AuthoringFeature().resolve(precompiled=None, validator=lambda _: Diagnostics(), session=session, request=_request(), decode_document=lambda _media, _content: connected_contract, decode_records=decode)
    assert result.contract is connected_contract
    assert seen == [{"id": "one"}, {"id": "two"}]
    assert result.progress[0].message == "started"
    assert result.diagnostics[0].code == "NOTE"


def test_record_stream_requires_advertised_streaming_support(connected_contract: Contract) -> None:
    session = FakeSession((AuthorIRRecord({"id": "one"}), AuthorComplete("job.a", "author:python:1")), streaming=False)
    with pytest.raises(AuthoringError) as caught:
        AuthoringFeature().resolve(precompiled=None, validator=lambda _: Diagnostics(), session=session, request=_request(), decode_document=lambda _media, _content: connected_contract, decode_records=lambda _: connected_contract)
    assert caught.value.code == "AUTHOR_STREAMING_UNSUPPORTED"
    assert session.cancelled == ["job.a"]


def test_document_output_uses_document_decoder(connected_contract: Contract) -> None:
    session = FakeSession((AuthorDocument("application/json", b"{}"), AuthorComplete("job.a", "author:python:1")))
    result = AuthoringFeature().resolve(precompiled=None, validator=lambda _: Diagnostics(), session=session, request=_request(), decode_document=lambda media, content: connected_contract if (media, content) == ("application/json", b"{}") else None, decode_records=lambda _: connected_contract)  # type: ignore[arg-type]
    assert result.contract is connected_contract


def test_precompiled_ir_bypasses_author_session(connected_contract: Contract) -> None:
    result = AuthoringFeature().resolve(precompiled=connected_contract, validator=lambda _: Diagnostics())
    assert result.precompiled
    assert result.hello is None


def test_invalid_authored_ir_is_rejected(connected_contract: Contract) -> None:
    invalid = Diagnostics((Diagnostic("IR_BAD", DiagnosticSeverity.ERROR, "bad"),))
    session = FakeSession((AuthorDocument("application/json", b"{}"), AuthorComplete("job.a", "author:python:1")))
    with pytest.raises(AuthoringError) as caught:
        AuthoringFeature().resolve(precompiled=None, validator=lambda _: invalid, session=session, request=_request(), decode_document=lambda _media, _content: connected_contract, decode_records=lambda _: connected_contract)
    assert caught.value.code == "AUTHOR_INVALID_IR"


def test_unsupported_ir_version_and_cancellation_fail_before_work(connected_contract: Contract) -> None:
    bad_request = AuthorRequest(1, "job.a", "2", "python", (AuthorSource("resource://project/author.py"),))
    session = FakeSession(())
    with pytest.raises(AuthoringError) as version:
        AuthoringFeature().resolve(precompiled=None, validator=lambda _: Diagnostics(), session=session, request=bad_request, decode_document=lambda _m, _c: connected_contract, decode_records=lambda _: connected_contract)
    assert version.value.code == "AUTHOR_IR_VERSION"

    session = FakeSession(())
    with pytest.raises(AuthoringError) as cancelled:
        AuthoringFeature().resolve(precompiled=None, validator=lambda _: Diagnostics(), session=session, request=_request(), decode_document=lambda _m, _c: connected_contract, decode_records=lambda _: connected_contract, is_cancelled=lambda: True)
    assert cancelled.value.code == "AUTHOR_CANCELLED"
    assert session.cancelled == ["job.a"]
