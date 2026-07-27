from __future__ import annotations

from dataclasses import dataclass
from typing import Final

import jinja2
from jinja2 import (
    TemplateAssertionError,
    TemplateNotFound,
    TemplateRuntimeError,
    TemplateSyntaxError,
    UndefinedError,
)
from jinja2.environment import Template
from jinja2.sandbox import SecurityError

from codepotg.api import CancellationToken, OperationCancelled
from codepotg.diagnostics import Diagnostic, Diagnostics
from codepotg.plugins import PluginCategory, PluginDescriptor, PluginTrust
from codepotg.ports import RenderRequest, RenderResult
from codepotg.versions import IR_API_VERSION, PLUGIN_API_VERSION, Version
from codepotg_template_jinja.caching import (
    BoundedCache,
    CacheStats,
    sha256_text,
    stable_identity,
)
from codepotg_template_jinja.context import ContextSafetyError, freeze_context
from codepotg_template_jinja.diagnostics import (
    error_diagnostic,
    failure_result_diagnostics,
    undefined_name,
)
from codepotg_template_jinja.helpers import (
    HelperConflictError,
    HelperDescriptor,
    HelperRegistry,
)
from codepotg_template_jinja.rules import JinjaEngineRules
from codepotg_template_jinja.sandbox import OutputAccumulator, RenderLimitError, create_environment
from codepotg_template_jinja.templates import (
    AnalysisResult,
    ImmutableRegistryLoader,
    TemplateAnalysisError,
    TemplateRegistry,
    TemplateRegistryError,
    analyze_dependencies,
)

PACKAGE_VERSION: Final = "2.0.0a1"
ENGINE_SEMVER: Final = "2.0.0-alpha.1"
ENGINE_BEHAVIOR_VERSION: Final = 1
SUFFIXES: Final = (".j2", ".jinja", ".jinja2")
CAPABILITIES: Final = (
    "context.immutable",
    "diagnostics.structured",
    "includes.declared",
    "inheritance.declared",
    "render.streaming",
    "sandbox.strict",
    "undefined.strict",
)

PLUGIN_DESCRIPTOR: Final = PluginDescriptor(
    id="jinja",
    category=PluginCategory.TEMPLATE_ENGINE,
    distribution="codepotg-template-jinja",
    version=Version.parse(ENGINE_SEMVER),
    api_version=PLUGIN_API_VERSION,
    ir_version=IR_API_VERSION,
    capabilities=CAPABILITIES,
    trust=PluginTrust.EXECUTABLE,
    documentation=(
        "https://github.com/alidantech-org/codepot/tree/"
        "chatgpt/codepotx-restart/packages/python/codepotg-template-jinja"
    ),
)


@dataclass(frozen=True, slots=True)
class _CompiledTemplate:
    identity: str
    template: Template


@dataclass(frozen=True, slots=True)
class _PreparedCompilation:
    registry: TemplateRegistry
    analysis: AnalysisResult
    identity: str


class JinjaTemplateEngine:
    """Strict deterministic adapter for the public CodepotG TemplateEngine port."""

    def __init__(
        self,
        *,
        rules: JinjaEngineRules | None = None,
        helpers: tuple[HelperDescriptor, ...] = (),
    ) -> None:
        startup: Diagnostic | None = None
        if rules is not None and not isinstance(rules, JinjaEngineRules):
            startup = error_diagnostic(
                "JINJA_RULE_INVALID",
                "engine rules must be a JinjaEngineRules value",
                template_id="<engine>",
                details={"rule_type": type(rules).__name__},
            )
            rules = JinjaEngineRules()
        self._rules = rules or JinjaEngineRules()
        try:
            self._helpers = HelperRegistry.create(helpers)
        except HelperConflictError as exc:
            startup = error_diagnostic(
                "JINJA_HELPER_CONFLICT",
                "registered Jinja helper names must be unique",
                template_id="<engine>",
                details={"helper_name": exc.name},
            )
            self._helpers = HelperRegistry(())
        self._startup_diagnostic = startup
        self._cache: BoundedCache[_CompiledTemplate] = BoundedCache(
            self._rules.cache_entries
        )

    @property
    def plugin(self) -> PluginDescriptor:
        return PLUGIN_DESCRIPTOR

    @property
    def suffixes(self) -> tuple[str, ...]:
        return SUFFIXES

    @property
    def rules(self) -> JinjaEngineRules:
        return self._rules

    @property
    def helper_descriptors(self) -> tuple[HelperDescriptor, ...]:
        return self._helpers.descriptors

    @property
    def cache_stats(self) -> CacheStats:
        return self._cache.stats()

    def clear_cache(self) -> None:
        self._cache.clear()

    def render(
        self,
        request: RenderRequest,
        cancellation: CancellationToken,
    ) -> RenderResult:
        template_id = request.template_id or "<invalid>"
        try:
            cancellation.raise_if_cancelled()
            if self._startup_diagnostic is not None:
                return self._failure(self._startup_diagnostic)

            registry = TemplateRegistry.create(request, self._rules)
            cancellation.raise_if_cancelled()
            context = freeze_context(request.context, self._rules)
            cancellation.raise_if_cancelled()

            prepared = self._prepare_compilation(registry, cancellation)
            compiled = self._cache.get(prepared.identity)
            if compiled is None:
                cancellation.raise_if_cancelled()
                compiled = self._compile(prepared)
                self._cache.put(prepared.identity, compiled)

            cancellation.raise_if_cancelled()
            output = OutputAccumulator(self._rules.max_render_bytes)
            render_values = dict(context.as_tuple())
            for chunk in compiled.template.generate(**render_values):
                cancellation.raise_if_cancelled()
                output.append(chunk)
            cancellation.raise_if_cancelled()
            return RenderResult(content=output.content(), diagnostics=Diagnostics())
        except OperationCancelled:
            return self._failure(
                error_diagnostic(
                    "JINJA_CANCELLED",
                    "Jinja rendering was cancelled",
                    template_id=template_id,
                    details={"reason": "cancelled", "template_id": template_id},
                )
            )
        except TemplateRegistryError as exc:
            return self._failure(
                error_diagnostic(
                    exc.code,
                    str(exc),
                    template_id=exc.template_id,
                    details=dict(exc.details),
                )
            )
        except ContextSafetyError as exc:
            return self._failure(
                error_diagnostic(
                    exc.code,
                    str(exc),
                    template_id=template_id,
                    details={
                        "context_path": exc.path,
                        "template_id": template_id,
                        "value_type": exc.value_type,
                    },
                )
            )
        except TemplateAnalysisError as exc:
            return self._failure(
                error_diagnostic(
                    exc.code,
                    str(exc),
                    template_id=exc.template_id,
                    line=exc.line,
                    details=dict(exc.details),
                )
            )
        except (TemplateSyntaxError, TemplateAssertionError) as exc:
            failed_id = getattr(exc, "name", None) or template_id
            return self._failure(
                error_diagnostic(
                    "JINJA_SYNTAX",
                    "template syntax is invalid",
                    template_id=failed_id,
                    line=getattr(exc, "lineno", None),
                    details={
                        "exception_type": type(exc).__name__,
                        "template_id": failed_id,
                    },
                )
            )
        except UndefinedError as exc:
            name = undefined_name(str(exc))
            details: dict[str, object] = {
                "exception_type": type(exc).__name__,
                "template_id": template_id,
            }
            if name is not None:
                details["undefined_name"] = name
            return self._failure(
                error_diagnostic(
                    "JINJA_UNDEFINED",
                    "template referenced an undefined value",
                    template_id=template_id,
                    details=details,
                )
            )
        except SecurityError as exc:
            message = str(exc)
            code = (
                "JINJA_CALLABLE_DENIED"
                if "not safely callable" in message
                else "JINJA_ATTRIBUTE_DENIED"
            )
            return self._failure(
                error_diagnostic(
                    code,
                    "template attempted a denied sandbox operation",
                    template_id=template_id,
                    details={
                        "exception_type": type(exc).__name__,
                        "template_id": template_id,
                    },
                )
            )
        except TemplateNotFound as exc:
            missing = str(exc.name)
            return self._failure(
                error_diagnostic(
                    "JINJA_INCLUDE_MISSING",
                    "declared template dependency could not be loaded",
                    template_id=template_id,
                    details={
                        "dependency_id": missing,
                        "exception_type": type(exc).__name__,
                        "template_id": template_id,
                    },
                )
            )
        except RenderLimitError as exc:
            return self._failure(
                error_diagnostic(
                    "JINJA_RENDER_LIMIT",
                    "rendered output exceeds the configured byte limit",
                    template_id=template_id,
                    details={
                        "actual_bytes": exc.actual_bytes,
                        "max_bytes": exc.max_bytes,
                        "template_id": template_id,
                    },
                )
            )
        except (TemplateRuntimeError, RecursionError, UnicodeError, TypeError, ValueError) as exc:
            return self._failure(
                error_diagnostic(
                    "JINJA_RUNTIME",
                    "template rendering failed safely",
                    template_id=template_id,
                    details={
                        "exception_type": type(exc).__name__,
                        "template_id": template_id,
                    },
                )
            )
        except Exception as exc:  # defensive adapter boundary; never expose a traceback
            return self._failure(
                error_diagnostic(
                    "JINJA_RUNTIME",
                    "template rendering failed safely",
                    template_id=template_id,
                    details={
                        "exception_type": type(exc).__name__,
                        "template_id": template_id,
                    },
                )
            )

    def compilation_identity(
        self,
        request: RenderRequest,
        cancellation: CancellationToken | None = None,
    ) -> str:
        """Return the deterministic compilation identity for host diagnostics/tests."""

        token = cancellation or CancellationToken()
        token.raise_if_cancelled()
        registry = TemplateRegistry.create(request, self._rules)
        prepared = self._prepare_compilation(registry, token)
        token.raise_if_cancelled()
        return prepared.identity

    def _prepare_compilation(
        self,
        registry: TemplateRegistry,
        cancellation: CancellationToken,
    ) -> _PreparedCompilation:
        cancellation.raise_if_cancelled()
        analysis_loader = ImmutableRegistryLoader(registry.selected(registry.partial_ids))
        analysis_environment = create_environment(
            loader=analysis_loader,
            rules=self._rules,
            helpers=self._helpers,
            cache_size=0,
        )
        cancellation.raise_if_cancelled()
        analysis = analyze_dependencies(
            analysis_environment,
            registry,
            self._rules,
            cancellation,
        )
        identity = self._cache_identity(registry, analysis)
        return _PreparedCompilation(registry, analysis, identity)

    def _compile(self, prepared: _PreparedCompilation) -> _CompiledTemplate:
        selected_sources = prepared.registry.selected(prepared.analysis.reachable_partial_ids)
        loader = ImmutableRegistryLoader(selected_sources)
        environment = create_environment(
            loader=loader,
            rules=self._rules,
            helpers=self._helpers,
            cache_size=max(1, len(selected_sources)),
        )
        template = environment.get_template(prepared.registry.root_id)
        return _CompiledTemplate(identity=prepared.identity, template=template)

    def _cache_identity(
        self,
        registry: TemplateRegistry,
        analysis: AnalysisResult,
    ) -> str:
        reachable = tuple(
            (partial_id, sha256_text(registry.source(partial_id)))
            for partial_id in analysis.reachable_partial_ids
        )
        return stable_identity(
            (
                ("package_version", PACKAGE_VERSION),
                ("engine_behavior_version", ENGINE_BEHAVIOR_VERSION),
                ("jinja_version", getattr(jinja2, "__version__", "3.1")),
                ("rules", self._rules.identity()),
                ("helpers", self._helpers.identity),
                ("root_id", registry.root_id),
                ("root_source", sha256_text(registry.root_source)),
                ("reachable_partials", reachable),
            )
        )

    @staticmethod
    def _failure(diagnostic: Diagnostic) -> RenderResult:
        return RenderResult(
            content=None,
            diagnostics=failure_result_diagnostics(diagnostic),
        )
