from __future__ import annotations

from codepotg.api import CancellationToken, OperationCancelled
from codepotg.ir import validate_contract
from codepotg.plugins import PluginDescriptor
from codepotg.ports import SourceAdapterRequest, SourceAdapterResult

from .diagnostics import DiagnosticBag
from .digest import DigestDocument, source_digest
from .loading.controlled_loader import ControlledSourceLoader, ReferenceLoader, SourceLoadError
from .loading.policy import SourcePolicy
from .normalization.pipeline import normalize_standard_contract
from .options import OpenApiOptions, OptionDecodeError
from .parsing.parser import DocumentParser
from .plugin import PLUGIN
from .references.resolver import ReferenceResolver
from .references.validation import validate_reference_graph


class OpenApiSourceAdapter:
    """Production OpenAPI source adapter using one isolated session per call."""

    def __init__(
        self,
        *,
        reference_loader: ReferenceLoader | None = None,
        source_policy: SourcePolicy | None = None,
    ) -> None:
        self._loader = ControlledSourceLoader(
            source_policy=source_policy or SourcePolicy(),
            reference_loader=reference_loader,
        )

    @property
    def plugin(self) -> PluginDescriptor:
        return PLUGIN

    def normalize(
        self,
        request: SourceAdapterRequest,
        cancellation: CancellationToken,
    ) -> SourceAdapterResult:
        diagnostics = DiagnosticBag()
        try:
            options = OpenApiOptions.decode(request.options)
            session = self._loader.new_session()
            cancellation.raise_if_cancelled()
            loaded_root = session.load_root(request, options, cancellation)
            parser = DocumentParser()
            root = parser.parse(
                loaded_root,
                diagnostics,
                require_openapi=True,
                options=options,
            )
            if root is None:
                return _failure(diagnostics)

            cancellation.raise_if_cancelled()
            resolver = ReferenceResolver(
                root=root,
                loader=session,
                parser=parser,
                options=options,
                diagnostics=diagnostics,
                cancellation=cancellation,
            )
            validate_reference_graph(root, resolver, cancellation)
            if diagnostics.has_errors:
                return _failure(diagnostics)

            contract = normalize_standard_contract(
                root=root,
                resolver=resolver,
                options=options,
                diagnostics=diagnostics,
                cancellation=cancellation,
            )
            if contract is None or diagnostics.has_errors:
                return _failure(diagnostics)

            cancellation.raise_if_cancelled()
            diagnostics.extend(validate_contract(contract))
            frozen_diagnostics = diagnostics.freeze()
            if frozen_diagnostics.has_errors:
                return SourceAdapterResult(
                    contract=None,
                    digest=None,
                    diagnostics=frozen_diagnostics,
                )

            digest = source_digest(
                documents=tuple(
                    DigestDocument(
                        identity=document.source.logical_id,
                        value=document.value,
                    )
                    for document in resolver.documents
                ),
                options=options,
                reference_authority=session.authority_id,
            )
            return SourceAdapterResult(
                contract=contract,
                digest=digest,
                diagnostics=frozen_diagnostics,
            )
        except OptionDecodeError as exc:
            diagnostics.error(
                "OA_OPTIONS_INVALID",
                str(exc),
                details=(("option", exc.key),),
            )
        except SourceLoadError as exc:
            diagnostics.error(exc.code, exc.message)
        except OperationCancelled:
            diagnostics.error(
                "OA_CANCELLED",
                "OpenAPI normalization was cancelled",
            )
        except Exception:
            diagnostics.fatal(
                "OA_INTERNAL_NORMALIZATION",
                "OpenAPI normalization failed inside the adapter boundary",
            )
        return _failure(diagnostics)


def _failure(diagnostics: DiagnosticBag) -> SourceAdapterResult:
    frozen = diagnostics.freeze()
    if not frozen.has_errors:
        diagnostics.error(
            "OA_NORMALIZATION_FAILED",
            "OpenAPI normalization did not produce a contract",
        )
        frozen = diagnostics.freeze()
    return SourceAdapterResult(contract=None, digest=None, diagnostics=frozen)
