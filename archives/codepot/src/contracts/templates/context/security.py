"""Security template context contracts."""

from __future__ import annotations

from dataclasses import dataclass

from archives.codepot.src.contracts.spec.refs import SpecRef
from archives.codepot.src.contracts.templates.context.base import TemplateBaseContext
from archives.codepot.src.contracts.templates.shared.items import (
    TemplateCollectionContext,
    TemplateItemContext,
)
from archives.codepot.src.spec.ir.security.definition import (
    SecurityCredentialDefinition,
    SecurityPolicyDefinition,
    SecurityPrincipalDefinition,
)


@dataclass(frozen=True)
class TemplateSecurityCredentialContext:
    """Template context for one security credential."""

    item: TemplateItemContext[SecurityCredentialDefinition]
    source: str
    key: str
    format: str | None = None
    value_type: SpecRef | None = None


@dataclass(frozen=True)
class TemplateSecurityPrincipalFieldContext:
    """Template context for one security principal field."""

    key: str
    ref: SpecRef


@dataclass(frozen=True)
class TemplateSecurityPrincipalContext:
    """Template context for one security principal."""

    item: TemplateItemContext[SecurityPrincipalDefinition]
    fields: tuple[TemplateSecurityPrincipalFieldContext, ...]


@dataclass(frozen=True)
class TemplateSecurityPolicyPrincipalContext:
    """Template context for one policy principal ref."""

    key: str
    ref: SpecRef


@dataclass(frozen=True)
class TemplateSecurityPolicyContext:
    """Template context for one security policy."""

    item: TemplateItemContext[SecurityPolicyDefinition]
    mode: str
    credential: SpecRef | None = None
    principals: tuple[TemplateSecurityPolicyPrincipalContext, ...] = ()
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    intent: str | None = None


@dataclass(frozen=True)
class TemplateSecurityCredentialsEachContext:
    """Context for ``select: security_credentials.each``."""

    base: TemplateBaseContext
    security_credential: TemplateSecurityCredentialContext
    item: TemplateSecurityCredentialContext


@dataclass(frozen=True)
class TemplateSecurityCredentialsAllContext:
    """Context for ``select: security_credentials.all``."""

    base: TemplateBaseContext
    security_credentials: tuple[TemplateSecurityCredentialContext, ...]
    items: TemplateCollectionContext[TemplateSecurityCredentialContext]


@dataclass(frozen=True)
class TemplateSecurityPrincipalsEachContext:
    """Context for ``select: security_principals.each``."""

    base: TemplateBaseContext
    security_principal: TemplateSecurityPrincipalContext
    item: TemplateSecurityPrincipalContext


@dataclass(frozen=True)
class TemplateSecurityPrincipalsAllContext:
    """Context for ``select: security_principals.all``."""

    base: TemplateBaseContext
    security_principals: tuple[TemplateSecurityPrincipalContext, ...]
    items: TemplateCollectionContext[TemplateSecurityPrincipalContext]


@dataclass(frozen=True)
class TemplateSecurityPoliciesEachContext:
    """Context for ``select: security_policies.each``."""

    base: TemplateBaseContext
    security_policy: TemplateSecurityPolicyContext
    item: TemplateSecurityPolicyContext


@dataclass(frozen=True)
class TemplateSecurityPoliciesAllContext:
    """Context for ``select: security_policies.all``."""

    base: TemplateBaseContext
    security_policies: tuple[TemplateSecurityPolicyContext, ...]
    items: TemplateCollectionContext[TemplateSecurityPolicyContext]
