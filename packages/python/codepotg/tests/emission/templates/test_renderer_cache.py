from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from emission.templates.renderer import (
    cached_environment,
    clear_environment_cache,
    render_template,
)


def test_cached_environment_is_reused_per_template_root(tmp_path: Path) -> None:
    clear_environment_cache()

    first = cached_environment(tmp_path)
    second = cached_environment(tmp_path)

    assert first is second
    clear_environment_cache()
    assert cached_environment(tmp_path) is not first
    clear_environment_cache()


def test_shared_environment_renders_concurrent_contexts(tmp_path: Path) -> None:
    template = tmp_path / "value.txt.j2"
    template.write_text("value={{ value }}\n", encoding="utf-8")
    clear_environment_cache()

    with ThreadPoolExecutor(max_workers=8) as pool:
        values = tuple(
            pool.map(
                lambda value: render_template(
                    tmp_path,
                    Path("value.txt.j2"),
                    {"value": value},
                ),
                range(64),
            )
        )

    assert values == tuple(f"value={value}\n" for value in range(64))
    clear_environment_cache()
