from __future__ import annotations

import importlib


main_module = importlib.import_module("dryv_cli.main")


def test_main_propagates_click_returned_exit_code(monkeypatch) -> None:
    monkeypatch.setattr(main_module.app, "main", lambda **_: 1)

    assert main_module.main([]) == 1


def test_main_normalizes_non_integer_click_result_to_success(monkeypatch) -> None:
    monkeypatch.setattr(main_module.app, "main", lambda **_: None)

    assert main_module.main([]) == 0
