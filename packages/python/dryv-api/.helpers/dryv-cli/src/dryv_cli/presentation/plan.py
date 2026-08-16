from __future__ import annotations

import json

from .console import Console


def render_plan(console: Console, plan: dict[str, object], *, full_json: bool = False) -> None:
    if full_json:
        console.write(json.dumps(plan, ensure_ascii=False, sort_keys=True, indent=2))
        return
    plan_hash = plan.get("planHash", "unknown")
    project = plan.get("projectName", "unknown")
    jobs = plan.get("jobs", [])
    artifacts = plan.get("artifacts", [])
    renderers = plan.get("requiredRenderers", [])
    console.write(f"Plan: {plan_hash}")
    console.write(f"Project: {project}")
    console.write(f"Jobs: {len(jobs) if isinstance(jobs, list) else '?'}")
    console.write(f"Artifacts: {len(artifacts) if isinstance(artifacts, list) else '?'}")
    if isinstance(renderers, list):
        console.write("Renderers: " + (", ".join(str(item) for item in renderers) or "none"))
    if isinstance(artifacts, list):
        for item in artifacts:
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                console.write(f"  {item['path']}")


__all__ = ["render_plan"]
