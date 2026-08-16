# HELPER-17 — CLI presentation and final commands

Status: TODO
Prerequisite: HELPER-16 DONE.
Review gate: ALL PRODUCTION-CODE REVIEW after completion.

## Goal
Finish the simple public Dryv experience over the modular Project Client/orchestration implementation.

## Required structure
Implement/finish `app/` (`app.py`, `arguments.py`, `context.py`), `commands/` (`validate.py`, `compile.py`, `plan.py`, `generate.py`) and `presentation/` (`console.py`, `diagnostics.py`, `progress.py`, `plan.py`, `changes.py`). Keep `__main__.py` a thin entrypoint.

Required UX:
- `dryv validate`: resolve/compile author source when needed and report author/canonical diagnostics without generation writes;
- `dryv compile`: compile author source to Canonical IR through the Author boundary using the approved representation/output behavior;
- `dryv plan`: obtain inputs and show API/Runtime GenerationPlan without applying files;
- `dryv generate`: full Author → API/Runtime → renderer → artifact → verified diff/apply flow;
- clear progress/errors while temporary local service/network details remain implementation plumbing.

## Enforcement
Presentation modules contain formatting only; commands compose existing modules rather than reimplement them. No old command flags/modes retained solely for compatibility. No hidden semantic defaults that contradict dryv.yaml/Runtime contracts. Keep output agent-friendly and deterministic where practical.

## Completion
The helper packages provide one coherent local user experience while retaining all architectural boundaries and local/remote substitutability.

## Mandatory stop
After this task, STOP. Perform production-code architecture review only. Do not add, modify, delete, regenerate or run tests until explicit approval starts the testing phase.