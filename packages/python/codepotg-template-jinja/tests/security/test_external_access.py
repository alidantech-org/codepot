from __future__ import annotations

import builtins
import os
import socket
import subprocess
from pathlib import Path

from codepotg_template_jinja import JinjaTemplateEngine

from tests.conftest import render


def _forbidden(*args: object, **kwargs: object) -> object:
    del args, kwargs
    raise AssertionError("host access was attempted")


def test_template_cannot_read_a_secret_file(tmp_path: Path, monkeypatch) -> None:
    secret = tmp_path / "secret.txt"
    secret.write_text("TOP-SECRET", encoding="utf-8")
    monkeypatch.setattr(builtins, "open", _forbidden)
    result = render(
        JinjaTemplateEngine(),
        "{{ open(secret_path).read() }}",
        context=(("secret_path", str(secret)),),
    )
    assert result.content is None
    assert "TOP-SECRET" not in str(result.diagnostics)


def test_template_cannot_read_environment_secret(monkeypatch) -> None:
    monkeypatch.setenv("CODEPOTG_JINJA_SECRET", "ENV-SECRET")
    result = render(JinjaTemplateEngine(), "{{ os.environ.CODEPOTG_JINJA_SECRET }}")
    assert result.content is None
    assert "ENV-SECRET" not in str(result.diagnostics)
    assert os.environ["CODEPOTG_JINJA_SECRET"] == "ENV-SECRET"


def test_template_cannot_execute_process(monkeypatch) -> None:
    monkeypatch.setattr(subprocess, "run", _forbidden)
    monkeypatch.setattr(subprocess, "Popen", _forbidden)
    result = render(JinjaTemplateEngine(), "{{ subprocess.run(('echo', 'escaped')) }}")
    assert result.content is None


def test_template_cannot_open_network_socket(monkeypatch) -> None:
    monkeypatch.setattr(socket, "socket", _forbidden)
    monkeypatch.setattr(socket, "create_connection", _forbidden)
    result = render(JinjaTemplateEngine(), "{{ socket.create_connection(('example.com', 80)) }}")
    assert result.content is None


def test_mutable_context_objects_are_rejected_without_mutation() -> None:
    value = {"safe": "value"}
    before = value.copy()
    result = render(JinjaTemplateEngine(), "{{ value.safe }}", context=(("value", value),))
    assert result.content is None
    assert value == before


def test_helper_registry_does_not_change_after_failure() -> None:
    engine = JinjaTemplateEngine()
    before = engine.helper_descriptors
    result = render(engine, "{{ value.__class__ }}", context=(("value", "x"),))
    assert result.content is None
    assert engine.helper_descriptors == before
