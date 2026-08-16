from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ApiEvent:
    type: str
    build_id: str | None
    sequence: int | None
    message: str | None
    subject: str | None
    details: dict[str, object]
    document: dict[str, object]

    @property
    def artifact(self) -> bool:
        return self.type.startswith("artifact.")


def decode_event(value: object) -> ApiEvent:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise ValueError("API event must be a JSON object")
    event_type = value.get("type")
    if not isinstance(event_type, str) or not event_type:
        raise ValueError("API event requires a type")
    sequence = value.get("sequence")
    if sequence is not None and (not isinstance(sequence, int) or isinstance(sequence, bool)):
        raise ValueError("API event sequence must be an integer")
    details = value.get("details", {})
    if not isinstance(details, dict) or not all(isinstance(key, str) for key in details):
        raise ValueError("API event details must be an object")
    return ApiEvent(
        event_type,
        value.get("buildId") if isinstance(value.get("buildId"), str) else None,
        sequence,
        value.get("message") if isinstance(value.get("message"), str) else None,
        value.get("subject") if isinstance(value.get("subject"), str) else None,
        dict(details),
        dict(value),
    )


__all__ = ["ApiEvent", "decode_event"]
