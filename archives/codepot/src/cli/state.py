"""Typer runtime state helpers."""

from __future__ import annotations

from typing import Protocol

import typer
from archives.codepot.src.app import (
    EmitRequest,
    EmitResult,
    InferRequest,
    InferResult,
    InspectRequest,
    InspectResult,
    TemplateInspectRequest,
    TemplateInspectResult,
    TemplateSelectionsRequest,
    TemplateSelectionsResult,
    TemplateValidateRequest,
    TemplateValidateResult,
    TemplateVarsRequest,
    TemplateVarsResult,
    ValidateRequest,
    ValidateResult,
)

RUNTIME_KEY = "runtime"


class RuntimeApi(Protocol):
    def validate(self, request: ValidateRequest) -> ValidateResult: ...

    def inspect(self, request: InspectRequest) -> InspectResult: ...

    def infer(self, request: InferRequest) -> InferResult: ...

    def emit(self, request: EmitRequest) -> EmitResult: ...

    def template_validate(self, request: TemplateValidateRequest) -> TemplateValidateResult: ...

    def template_inspect(self, request: TemplateInspectRequest) -> TemplateInspectResult: ...

    def template_vars(self, request: TemplateVarsRequest) -> TemplateVarsResult: ...

    def template_selections(
        self,
        request: TemplateSelectionsRequest,
    ) -> TemplateSelectionsResult: ...


def set_runtime(ctx: typer.Context, runtime: RuntimeApi) -> None:
    if ctx.obj is None:
        ctx.obj = {}
    ctx.obj[RUNTIME_KEY] = runtime


def get_runtime(ctx: typer.Context) -> RuntimeApi:
    if ctx.obj is None or RUNTIME_KEY not in ctx.obj:
        raise RuntimeError("CLI runtime was not initialized.")
    return ctx.obj[RUNTIME_KEY]
