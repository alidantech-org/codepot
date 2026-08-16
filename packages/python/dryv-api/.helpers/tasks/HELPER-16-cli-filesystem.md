# HELPER-16 — CLI filesystem diff, staging and apply

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-15 DONE.

## Implemented boundary
`filesystem/` is the single helper owner of generated project-file mutation. It validates project-relative paths, reserves `.dryv/` for client state, loads explicit `dryv.managed/v1` metadata, hashes current files, and classifies CREATE / UPDATE / UNCHANGED / CONFLICT before mutation.

A previously managed file is updated only when its current bytes still match the recorded generated hash. Existing unmanaged files and locally modified managed files conflict by default; explicit `force` changes only regular-file conflicts into updates. No managed deletions are synthesized.

Writes are staged outside the project tree but on the same parent filesystem, applied with `os.replace`, existing updates are backed up, managed state is written atomically last, and failures attempt rollback without claiming success.

## Review hardening
Generated symlink targets and a symlinked managed-state file are rejected. Apply re-checks every target and the managed-state snapshot after staging and immediately before mutation, verifies resulting bytes against the verified artifacts before committing state, and removes stale state temp files on failure. `--force` does not authorize overwriting a file that changed after the diff was prepared.

## Completion
Verified artifacts can be diffed and safely applied with explicit outcomes. No other helper layer writes generated project files. Production source was reviewed; executable test certification remains separate.
