from __future__ import annotations

import json
from importlib.metadata import entry_points

from codepotg.api import CancellationToken
from codepotg.ports import SourceAdapter, SourceAdapterRequest


def test_registered_entry_point_loads_and_normalizes() -> None:
    entries = entry_points(group="codepotg.source_adapters")
    entry = next(item for item in entries if item.name == "openapi")
    adapter = entry.load()()
    assert isinstance(adapter, SourceAdapter)
    result = adapter.normalize(
        SourceAdapterRequest(
            source_id="entry-point",
            content=json.dumps(
                {
                    "openapi": "3.1.0",
                    "info": {"title": "Entry Point", "version": "1"},
                    "paths": {},
                }
            ),
        ),
        CancellationToken(),
    )
    assert result.contract is not None
    assert result.digest
    assert not result.diagnostics.has_errors
