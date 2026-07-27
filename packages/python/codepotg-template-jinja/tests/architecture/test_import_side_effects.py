from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]


def test_import_and_factory_do_not_scan_compile_or_mutate_environment(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-be-read.jinja"
    marker.write_text("{% invalid", encoding="utf-8")
    script = """
import os
before = dict(os.environ)
import codepotg_template_jinja
from codepotg_template_jinja.plugin import create_plugin
engine = create_plugin()
assert engine.cache_stats.entries == 0
assert dict(os.environ) == before
assert engine.suffixes == ('.j2', '.jinja', '.jinja2')
"""
    environment = dict(os.environ)
    source_path = str(PACKAGE_ROOT / "src")
    environment["PYTHONPATH"] = os.pathsep.join(
        item for item in (source_path, environment.get("PYTHONPATH", "")) if item
    )
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=tmp_path,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
