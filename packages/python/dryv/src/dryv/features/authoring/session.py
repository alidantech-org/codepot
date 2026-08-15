from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Iterator, Protocol

from dryv.diagnostics import Diagnostics
from dryv.ir import Contract

AUTHOR_PROTOCOL_VERSION = 1


class AuthoringError(ValueError):
    def __init__(self, code: str, message: str, *, job_id: str | None = None, validation: Diagnostics | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.job_id = job_id
        self.validation = validation


@dataclass(frozen=True, slots=True)
class AuthorBackendHello:
    backend_id: str
    backend_version: str
    supported_source_kinds: tuple[str, ...]
    supported_ir_versions: tuple[str, ...]
    protocol_versions: tuple[int, ...]
    streaming: bool
    fingerprint: str
    max_concurrency: int = 1

    def __post_init__(self) -> None:
        if not self.backend_id or not self.backend_version or not self.fingerprint:
            raise ValueError("author backend hello requires identity, version and fingerprint")
        if self.max_concurrency < 1:
            raise ValueError("author backend max_concurrency must be positive")
        for values in (self.supported_source_kinds, self.supported_ir_versions, self.protocol_versions):
            if len(values) != len(set(values)):
                raise ValueError("author capability collections must be unique")


@dataclass(frozen=True, slots=True)
class AuthorSource:
    resource_id: str
    media_type: str | None = None

    def __post_init__(self) -> None:
        if not self.resource_id or self.resource_id.strip() != self.resource_id:
            raise ValueError("author source resource id must be non-empty and trimmed")
        if self.media_type is not None and (not self.media_type or self.media_type.strip() != self.media_type):
            raise ValueError("author source media type must be non-empty and trimmed")


@dataclass(frozen=True, slots=True)
class AuthorRequest:
    protocol_version: int
    job_id: str
    requested_ir_version: str
    source_kind: str
    sources: tuple[AuthorSource, ...]
    options: tuple[tuple[str, object], ...] = ()

    def __post_init__(self) -> None:
        if self.protocol_version < 1:
            raise ValueError("author protocol version must be positive")
        if not self.job_id or not self.requested_ir_version or not self.source_kind:
            raise ValueError("author requests require job id, IR version and source kind")
        if not self.sources:
            raise ValueError("author requests require at least one logical source resource")
        source_ids = tuple(item.resource_id for item in self.sources)
        if len(source_ids) != len(set(source_ids)):
            raise ValueError("author source resource ids must be unique")
        option_names = tuple(name for name, _ in self.options)
        if tuple(sorted(option_names)) != option_names or len(option_names) != len(set(option_names)):
            raise ValueError("author options must be sorted by unique name")


@dataclass(frozen=True, slots=True)
class AuthorProgress:
    message: str
    completed: int | None = None
    total: int | None = None


@dataclass(frozen=True, slots=True)
class AuthorDiagnostic:
    code: str
    message: str
    severity: str = "error"


@dataclass(frozen=True, slots=True)
class AuthorIRRecord:
    record: object


@dataclass(frozen=True, slots=True)
class AuthorDocument:
    media_type: str
    content: bytes


@dataclass(frozen=True, slots=True)
class AuthorComplete:
    job_id: str
    backend_fingerprint: str


AuthorMessage = AuthorProgress | AuthorDiagnostic | AuthorIRRecord | AuthorDocument | AuthorComplete


class AuthorSession(Protocol):
    def hello(self) -> AuthorBackendHello: ...
    def author(self, request: AuthorRequest) -> Iterable[AuthorMessage]: ...
    def cancel(self, job_id: str) -> None: ...


@dataclass(frozen=True, slots=True)
class AuthoringResult:
    contract: Contract
    hello: AuthorBackendHello | None
    progress: tuple[AuthorProgress, ...]
    diagnostics: tuple[AuthorDiagnostic, ...]
    validation: Diagnostics
    precompiled: bool = False


class AuthoringFeature:
    def resolve(
        self,
        *,
        precompiled: Contract | None,
        validator: Callable[[Contract], Diagnostics],
        session: AuthorSession | None = None,
        request: AuthorRequest | None = None,
        decode_document: Callable[[str, bytes], Contract] | None = None,
        decode_records: Callable[[Iterable[object]], Contract] | None = None,
        is_cancelled: Callable[[], bool] | None = None,
    ) -> AuthoringResult:
        if precompiled is not None:
            validation = validator(precompiled)
            self._require_valid(validation, request.job_id if request is not None else None)
            return AuthoringResult(precompiled, None, (), (), validation, precompiled=True)
        if session is None or request is None or decode_document is None or decode_records is None:
            raise AuthoringError("AUTHOR_SESSION_REQUIRED", "author-backed source requires a session, request and canonical decoders")
        return self._author(session, request, validator, decode_document, decode_records, is_cancelled)

    def _author(
        self,
        session: AuthorSession,
        request: AuthorRequest,
        validator: Callable[[Contract], Diagnostics],
        decode_document: Callable[[str, bytes], Contract],
        decode_records: Callable[[Iterable[object]], Contract],
        is_cancelled: Callable[[], bool] | None,
    ) -> AuthoringResult:
        hello = session.hello()
        self._validate_hello(hello, request)
        self._raise_if_cancelled(session, request.job_id, is_cancelled, before_submission=True)

        progress: list[AuthorProgress] = []
        diagnostics: list[AuthorDiagnostic] = []
        messages = iter(session.author(request))
        complete: list[AuthorComplete] = []

        first_data: AuthorIRRecord | AuthorDocument | None = None
        for message in messages:
            self._raise_if_cancelled(session, request.job_id, is_cancelled)
            if isinstance(message, AuthorProgress):
                progress.append(message)
            elif isinstance(message, AuthorDiagnostic):
                diagnostics.append(message)
            elif isinstance(message, AuthorComplete):
                complete.append(message)
                break
            else:
                first_data = message
                break

        if first_data is None:
            raise AuthoringError("AUTHOR_NO_IR", "author backend completed without canonical IR", job_id=request.job_id)

        if isinstance(first_data, AuthorDocument):
            contract = decode_document(first_data.media_type, first_data.content)
            self._consume_tail(messages, session, request, progress, diagnostics, complete, is_cancelled)
        else:
            if not hello.streaming:
                session.cancel(request.job_id)
                raise AuthoringError("AUTHOR_STREAMING_UNSUPPORTED", "author backend returned record streaming without advertising streaming support", job_id=request.job_id)
            records = self._record_stream(first_data, messages, session, request, progress, diagnostics, complete, is_cancelled)
            contract = decode_records(records)

        self._raise_if_cancelled(session, request.job_id, is_cancelled)
        if not complete:
            raise AuthoringError("AUTHOR_INCOMPLETE", "author backend did not send completion", job_id=request.job_id)
        final = complete[-1]
        if final.job_id != request.job_id:
            raise AuthoringError("AUTHOR_JOB_MISMATCH", "author backend completed a different job", job_id=request.job_id)
        if final.backend_fingerprint != hello.fingerprint:
            raise AuthoringError("AUTHOR_FINGERPRINT_MISMATCH", "author backend fingerprint changed during the job", job_id=request.job_id)
        validation = validator(contract)
        self._require_valid(validation, request.job_id)
        return AuthoringResult(contract, hello, tuple(progress), tuple(diagnostics), validation)

    @staticmethod
    def _record_stream(
        first: AuthorIRRecord,
        messages: Iterator[AuthorMessage],
        session: AuthorSession,
        request: AuthorRequest,
        progress: list[AuthorProgress],
        diagnostics: list[AuthorDiagnostic],
        complete: list[AuthorComplete],
        is_cancelled: Callable[[], bool] | None,
    ) -> Iterator[object]:
        yield first.record
        for message in messages:
            AuthoringFeature._raise_if_cancelled(session, request.job_id, is_cancelled)
            if isinstance(message, AuthorIRRecord):
                yield message.record
            elif isinstance(message, AuthorProgress):
                progress.append(message)
            elif isinstance(message, AuthorDiagnostic):
                diagnostics.append(message)
            elif isinstance(message, AuthorDocument):
                raise AuthoringError("AUTHOR_MIXED_IR", "author backend mixed document and record outputs", job_id=request.job_id)
            elif isinstance(message, AuthorComplete):
                complete.append(message)
                return

    @staticmethod
    def _consume_tail(
        messages: Iterator[AuthorMessage],
        session: AuthorSession,
        request: AuthorRequest,
        progress: list[AuthorProgress],
        diagnostics: list[AuthorDiagnostic],
        complete: list[AuthorComplete],
        is_cancelled: Callable[[], bool] | None,
    ) -> None:
        for message in messages:
            AuthoringFeature._raise_if_cancelled(session, request.job_id, is_cancelled)
            if isinstance(message, AuthorProgress):
                progress.append(message)
            elif isinstance(message, AuthorDiagnostic):
                diagnostics.append(message)
            elif isinstance(message, AuthorComplete):
                complete.append(message)
                return
            else:
                raise AuthoringError("AUTHOR_MULTIPLE_IR", "author backend returned more than one canonical IR representation", job_id=request.job_id)

    @staticmethod
    def _validate_hello(hello: AuthorBackendHello, request: AuthorRequest) -> None:
        if request.protocol_version not in hello.protocol_versions:
            raise AuthoringError("AUTHOR_PROTOCOL_MISMATCH", "author backend does not support requested protocol", job_id=request.job_id)
        if request.requested_ir_version not in hello.supported_ir_versions:
            raise AuthoringError("AUTHOR_IR_VERSION", "author backend does not support requested IR version", job_id=request.job_id)
        if request.source_kind not in hello.supported_source_kinds:
            raise AuthoringError("AUTHOR_SOURCE_KIND", f"author backend does not support source kind {request.source_kind!r}", job_id=request.job_id)

    @staticmethod
    def _raise_if_cancelled(
        session: AuthorSession,
        job_id: str,
        is_cancelled: Callable[[], bool] | None,
        *,
        before_submission: bool = False,
    ) -> None:
        if is_cancelled is None or not is_cancelled():
            return
        session.cancel(job_id)
        phase = " before submission" if before_submission else ""
        raise AuthoringError("AUTHOR_CANCELLED", f"author job was cancelled{phase}", job_id=job_id)

    @staticmethod
    def _require_valid(validation: Diagnostics, job_id: str | None) -> None:
        if validation.has_errors:
            raise AuthoringError("AUTHOR_INVALID_IR", "author backend produced invalid Canonical Dryv IR", job_id=job_id, validation=validation)


__all__ = [
    "AUTHOR_PROTOCOL_VERSION",
    "AuthorBackendHello",
    "AuthorComplete",
    "AuthorDiagnostic",
    "AuthorDocument",
    "AuthorIRRecord",
    "AuthorMessage",
    "AuthorProgress",
    "AuthorRequest",
    "AuthorSession",
    "AuthorSource",
    "AuthoringError",
    "AuthoringFeature",
    "AuthoringResult",
]
