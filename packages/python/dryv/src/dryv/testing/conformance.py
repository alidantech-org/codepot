from __future__ import annotations

from dryv.api import CancellationToken
from dryv.ports import (
    IdentifierValidationRequest,
    ModulePathRequest,
    OutputPathValidationRequest,
    RenderRequest,
    SourceAdapter,
    SourceAdapterRequest,
    TargetAdapter,
    TemplateEngine,
)


def assert_source_adapter_conformance(
    adapter: SourceAdapter,
    request: SourceAdapterRequest,
) -> None:
    first = adapter.normalize(request, CancellationToken())
    second = adapter.normalize(request, CancellationToken())
    assert first == second, "source adapters must be deterministic"
    if first.contract is not None:
        assert first.digest, "normalized contracts require stable digests"
    else:
        assert first.diagnostics.has_errors


def assert_target_adapter_conformance(
    adapter: TargetAdapter,
    *,
    identifier: IdentifierValidationRequest,
    output_path: OutputPathValidationRequest,
    module_path: ModulePathRequest,
) -> None:
    assert adapter.targets, "target adapters must declare at least one target"
    assert tuple(sorted(adapter.targets, key=lambda item: item.id)) == adapter.targets
    assert adapter.validate_identifier(identifier) == adapter.validate_identifier(identifier)
    assert adapter.validate_output_path(output_path) == adapter.validate_output_path(output_path)
    assert adapter.resolve_module_path(module_path) == adapter.resolve_module_path(module_path)


def assert_template_engine_conformance(
    engine: TemplateEngine,
    request: RenderRequest,
) -> None:
    assert engine.suffixes, "template engines must declare at least one suffix"
    assert tuple(sorted(set(engine.suffixes))) == engine.suffixes
    first = engine.render(request, CancellationToken())
    second = engine.render(request, CancellationToken())
    assert first == second, "template engines must render deterministically"
    if first.content is None:
        assert first.diagnostics.has_errors
