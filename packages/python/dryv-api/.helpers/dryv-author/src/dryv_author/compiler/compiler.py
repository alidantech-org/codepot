from __future__ import annotations

from dataclasses import dataclass

from dryv.ir import Contract, Name, SemanticId, validate_contract
from dryv.ir.diagnostics import Diagnostics

from dryv_author.core import RefKind, contract_id
from dryv_author.features.events import compile_event
from dryv_author.features.failures import compile_failure
from dryv_author.features.groups import assemble_groups
from dryv_author.features.operations import compile_operation
from dryv_author.features.policies import compile_policy
from dryv_author.features.presentations import compile_presentation
from dryv_author.features.properties import compile_property
from dryv_author.features.schemas import compile_schema
from dryv_author.features.sources import compile_value_source
from dryv_author.features.storage import compile_storage
from dryv_author.features.views import compile_view
from dryv_author.features.workflows import compile_workflow

from .context import CompilerContext
from .passes import register, resolve, validate


@dataclass(frozen=True, slots=True)
class AuthoringResult:
    contract: Contract | None
    diagnostics: Diagnostics

    @property
    def ok(self) -> bool:
        return self.contract is not None and not self.diagnostics.has_errors


_FEATURE_COMPILERS = ((RefKind.PROPERTY, compile_property), (RefKind.SCHEMA, compile_schema), (RefKind.FAILURE, compile_failure), (RefKind.EVENT, compile_event), (RefKind.POLICY, compile_policy), (RefKind.OPERATION, compile_operation), (RefKind.STORAGE, compile_storage), (RefKind.VALUE_SOURCE, compile_value_source), (RefKind.VIEW, compile_view), (RefKind.WORKFLOW, compile_workflow), (RefKind.PRESENTATION, compile_presentation))


def compile_author(author: object) -> AuthoringResult:
    from dryv_author.api.author import Author
    if not isinstance(author, Author):
        raise TypeError("compile_author expects an Author")
    context = CompilerContext(author.metadata, author.registry)
    try:
        register(context)
        validate(context)
        if not context.diagnostics.has_errors:
            resolve(context)
        if not context.diagnostics.has_errors:
            _compile_features(context)
        if context.diagnostics.has_errors:
            return AuthoringResult(None, context.diagnostics)
        groups = assemble_groups(context)
        workflows = context.compiled_for(context.declarations(RefKind.WORKFLOW), RefKind.WORKFLOW)
        presentations = context.compiled_for(context.declarations(RefKind.PRESENTATION), RefKind.PRESENTATION)
        contract = Contract(SemanticId(contract_id(author.metadata.name)), Name(author.metadata.name), groups, version=author.metadata.version, presentations=presentations, workflows=workflows)
        canonical = validate_contract(contract)
        diagnostics = context.diagnostics.extend(canonical)
        return AuthoringResult(None if diagnostics.has_errors else contract, diagnostics)
    except Exception as exc:
        context.error("AUTHOR_COMPILE_FAILED", str(exc) or type(exc).__name__)
        return AuthoringResult(None, context.diagnostics)


def _compile_features(context: CompilerContext) -> None:
    for kind, compiler in _FEATURE_COMPILERS:
        for declaration in context.declarations(kind):
            context.put_compiled(declaration, compiler(context, declaration))


__all__ = ["AuthoringResult", "compile_author"]
