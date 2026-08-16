from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from dryv_cli.connections.api import ApiEvent


@dataclass(frozen=True, slots=True)
class GenerationProgress:
    type: str
    sequence: int | None
    message: str | None
    subject: str | None
    details: dict[str, object]


ProgressSink = Callable[[GenerationProgress], None]


def publish_events(events: Iterable[ApiEvent], sink: ProgressSink | None = None) -> Iterable[ApiEvent]:
    last_sequence = 0
    for event in events:
        if event.sequence is not None:
            if event.sequence <= last_sequence:
                raise RuntimeError("dryv-api build event sequence is not strictly increasing")
            last_sequence = event.sequence
        if sink is not None:
            sink(
                GenerationProgress(
                    event.type,
                    event.sequence,
                    event.message,
                    event.subject,
                    dict(event.details),
                )
            )
        yield event


__all__ = ["GenerationProgress", "ProgressSink", "publish_events"]
