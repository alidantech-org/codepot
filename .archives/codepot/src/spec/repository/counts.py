"""Spec repository count builder."""

from __future__ import annotations

from archives.codepot.src.contracts.spec.context import SpecCounts
from archives.codepot.src.contracts.spec.records import SpecRecord
from archives.codepot.src.spec.utils.enums import SpecSubject


def _count(
    records_by_subject: dict[SpecSubject, tuple[SpecRecord[object], ...]],
    subject: SpecSubject,
) -> int:
    """Return record count for a subject."""

    return len(records_by_subject[subject])


def build_counts(
    records_by_subject: dict[SpecSubject, tuple[SpecRecord[object], ...]],
) -> SpecCounts:
    """Build normalized spec counts from repository records."""

    primitives = _count(records_by_subject, SpecSubject.PRIMITIVES)
    enums = _count(records_by_subject, SpecSubject.ENUMS)
    composites = _count(records_by_subject, SpecSubject.COMPOSITES)

    entities = _count(records_by_subject, SpecSubject.ENTITIES)
    field_sets = _count(records_by_subject, SpecSubject.FIELD_SETS)
    models = _count(records_by_subject, SpecSubject.MODELS)
    dtos = _count(records_by_subject, SpecSubject.DTOS)
    params = _count(records_by_subject, SpecSubject.PARAMS)

    credentials = _count(records_by_subject, SpecSubject.SECURITY_CREDENTIALS)
    principals = _count(records_by_subject, SpecSubject.SECURITY_PRINCIPALS)
    policies = _count(records_by_subject, SpecSubject.SECURITY_POLICIES)

    errors = _count(records_by_subject, SpecSubject.ERRORS)

    return SpecCounts(
        urls=_count(records_by_subject, SpecSubject.URLS),
        content_types=_count(records_by_subject, SpecSubject.CONTENT_TYPES),
        primitives=primitives,
        enums=enums,
        composites=composites,
        entities=entities,
        field_sets=field_sets,
        models=models,
        dtos=dtos,
        params=params,
        resources=_count(records_by_subject, SpecSubject.RESOURCES),
        operations=_count(records_by_subject, SpecSubject.OPERATIONS),
        route_paths=_count(records_by_subject, SpecSubject.ROUTE_PATHS),
        routes=_count(records_by_subject, SpecSubject.ROUTES),
        errors=errors,
        security_credentials=credentials,
        security_principals=principals,
        security_policies=policies,
        properties_total=primitives + enums + composites,
        schemas_total=entities + field_sets + models + dtos + params,
        security_total=credentials + principals + policies,
        records_total=sum(len(records) for records in records_by_subject.values()),
    )
