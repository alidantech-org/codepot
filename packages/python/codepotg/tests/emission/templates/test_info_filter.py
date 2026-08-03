from __future__ import annotations

from pathlib import Path

from emission.templates.renderer import render_template


def test_info_comment_filter_renders_categories(tmp_path: Path) -> None:
    template = tmp_path / "comment.txt.j2"
    template.write_text("/*\n{{ info | info_comment }}\n */\n", encoding="utf-8")

    output = render_template(
        template_root=tmp_path,
        relative_path=Path("comment.txt.j2"),
        context={
            "info": {
                "implement": ("Use auth context.",),
                "warn": ("Never expose keyHash.",),
                "tenantSafety": ("Scope reads by tenant.",),
            }
        },
    )

    assert " * Implement:" in output
    assert " * - Use auth context." in output
    assert " * Warn:" in output
    assert " * Tenantsafety:" in output
