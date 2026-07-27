# Human validation: connected CodepotG v2 project

This workspace is intentionally not a pytest fixture. It is a small real project that a developer can inspect, modify, generate, compile, break, and recover manually.

It exercises the currently connectable path:

```text
Python using public codepotg.ir
    -> canonical Codepot IR JSON and YAML
    -> built-in ir source adapter
    -> codepotg.yaml
    -> two local CodepotgPack.yaml packs
    -> fixed selectors and complete artifact planning
    -> sandboxed Jinja rendering
    -> TypeScript and Dart target adapters
    -> memory output
    -> managed transactional files
    -> tsc and dart analyze
```

It does not hide the two current ecosystem gaps:

- `codepotg-author` can create typed declarations and refs, but does not compile a `Contract` yet.
- `codepotg-openapi` advertises an entry point whose factory imports a missing `codepotg_openapi.adapter` module.

## 1. Use the correct branch

From Git Bash at the repository root:

```bash
git fetch origin
git switch chatgpt/codepotx-restart-orchestrator
git pull --ff-only

git branch --show-current
git rev-parse HEAD
```

Do not run this workspace from `chatgpt/codepotx-restart` until the orchestrator branch has been independently verified and merged.

## 2. Create a clean manual-test environment

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

py -3.12 -m venv .venv-codepotg-manual
source .venv-codepotg-manual/Scripts/activate

python -m pip install --upgrade pip
python -m pip uninstall -y codepotg-openapi
python -m pip install \
  -e "$REPO_ROOT/packages/python/codepotg-v2" \
  -e "$REPO_ROOT/packages/python/codepotg-template-jinja" \
  -e "$REPO_ROOT/packages/python/codepotg-language-typescript" \
  -e "$REPO_ROOT/packages/python/codepotg-language-dart"
```

The OpenAPI package is deliberately excluded because its current broken factory can prevent discovery of every plugin, even when the project uses only canonical IR.

Move into this project:

```bash
cd "$REPO_ROOT/packages/python/codepotg-v2/examples/manual/connected-project"
```

## 3. Verify the installed plugin graph

```bash
python verify_plugins.py
```

Expected loaded plugin IDs:

```text
sources: ir
targets: typescript, dart
engines: jinja
```

The order may differ, but every required ID must appear exactly once.

## 4. Author and inspect the neutral contract

```bash
python bootstrap_contract.py
```

Expected files:

```text
contract.codepot.json
contract.codepot.yaml
```

The script validates the contract and asserts exact JSON and YAML round trips before returning success.

Human checks:

```bash
sed -n '1,120p' contract.codepot.yaml
sed -n '1,80p' contract.codepot.json
```

Confirm that the transport contains neutral schemas, fields, tags, and guidance, but no TypeScript, Dart, framework, ORM, controller, widget, or folder-layout semantics.

## 5. Inspect the complete plan before rendering

```bash
codepotg plan codepotg.yaml | tee plan.json
```

Expected artifact count: **12**.

Expected TypeScript paths:

```text
generated/typescript/package.json
generated/typescript/tsconfig.json
generated/typescript/src/models/user.ts
generated/typescript/src/models/ticket.ts
generated/typescript/src/enums/role.ts
generated/typescript/src/index.ts
```

Expected Dart paths:

```text
generated/dart/pubspec.yaml
generated/dart/analysis_options.yaml
generated/dart/lib/models/user.dart
generated/dart/lib/models/ticket.dart
generated/dart/lib/enums/role.dart
generated/dart/lib/manual_sdk.dart
```

Inspect that the barrel/library artifacts are planned after their provider selections and that every rendered source file has the correct target ID.

## 6. Render without writing

```bash
codepotg generate codepotg.yaml --memory | tee memory-output.json
```

Confirm that `generated` contains 12 in-memory artifacts and no project files have been created yet:

```bash
test ! -d generated
```

## 7. Generate real files

```bash
codepotg generate codepotg.yaml | tee write-report.json
find generated -type f | sort
```

Also inspect:

```bash
find .codepotg -type f -maxdepth 2 -print
sed -n '1,220p' .codepotg/generation-state.json
```

Human review targets:

```bash
sed -n '1,200p' generated/typescript/src/models/user.ts
sed -n '1,200p' generated/typescript/src/index.ts
sed -n '1,200p' generated/dart/lib/models/user.dart
sed -n '1,200p' generated/dart/lib/manual_sdk.dart
```

Confirm:

- the banner option and `contractSource` binding appear in generated comments;
- `domain:audited` changes only the authored template comment;
- nullable/optional field behavior differs correctly between TypeScript and Dart;
- every import/export statement came from a template;
- module specifiers were supplied as planned facts.

## 8. Prove deterministic regeneration

Run this before installing npm or Dart dependencies:

```bash
find generated -type f -print0 | sort -z | xargs -0 sha256sum > before.sha256
codepotg generate codepotg.yaml > rerun-report.json
find generated -type f -print0 | sort -z | xargs -0 sha256sum > after.sha256
diff -u before.sha256 after.sha256
```

Expected: no hash differences.

## 9. Compile the generated TypeScript project

```bash
cd generated/typescript
npm install
npm run typecheck
cd ../..
```

Expected: `tsc --noEmit` succeeds without editing generated code.

## 10. Analyze the generated Dart package

A Dart 3.3+ SDK must be installed and available on `PATH`.

```bash
cd generated/dart
dart pub get
dart format --output=none --set-exit-if-changed lib
dart analyze
cd ../..
```

Expected: formatting and analysis succeed without editing generated code.

## 11. Prove managed-file edit protection

```bash
cp generated/typescript/src/models/user.ts /tmp/codepotg-user.ts
printf '\n// HUMAN EDIT THAT MUST BE PROTECTED\n' >> generated/typescript/src/models/user.ts

codepotg generate codepotg.yaml
GENERATION_EXIT=$?
echo "exit=$GENERATION_EXIT"
tail -n 4 generated/typescript/src/models/user.ts
```

Expected:

- non-zero generation exit;
- the human edit remains present;
- CodepotG does not overwrite the modified managed file.

Recover:

```bash
cp /tmp/codepotg-user.ts generated/typescript/src/models/user.ts
codepotg generate codepotg.yaml
```

## 12. Prove stale managed-file deletion

Generate a contract without the `Ticket` schema:

```bash
python bootstrap_contract.py --without-ticket
codepotg generate codepotg.yaml

test ! -f generated/typescript/src/models/ticket.ts
test ! -f generated/dart/lib/models/ticket.dart
```

Expected: both unchanged, stale, managed files are deleted.

Restore the full contract:

```bash
python bootstrap_contract.py
codepotg generate codepotg.yaml
```

## 13. Prove unmanaged collision protection

```bash
rm -rf collision-output
mkdir -p collision-output/generated/typescript/src/models
printf 'UNMANAGED HUMAN FILE\n' > collision-output/generated/typescript/src/models/user.ts

codepotg generate codepotg.yaml --destination collision-output
COLLISION_EXIT=$?
echo "exit=$COLLISION_EXIT"
cat collision-output/generated/typescript/src/models/user.ts
```

Expected:

- non-zero generation exit;
- the unmanaged file is unchanged;
- no partial project is committed around the collision.

## 14. Inspect the current `codepotg-author` boundary

Install it only for this separate probe:

```bash
python -m pip install -e "$REPO_ROOT/packages/python/codepotg-author"
python audit_authoring_gap.py
```

Expected current result: typed declarations and refs are created, followed by an explicit message that no `Author.compile()` path exists yet.

This is not the desired final authoring workflow. It records the exact present boundary so the package cannot be called complete prematurely.

## 15. Reproduce the current OpenAPI blocker

Do this last because installing the package intentionally poisons automatic source-adapter discovery in the current implementation:

```bash
python -m pip install -e "$REPO_ROOT/packages/python/codepotg-openapi"
python -c 'from codepotg_openapi.plugin import create_plugin; create_plugin()'
```

Expected current failure:

```text
ModuleNotFoundError: No module named 'codepotg_openapi.adapter'
```

Remove it before continuing with the working IR path:

```bash
python -m pip uninstall -y codepotg-openapi
python verify_plugins.py
```

## 16. Installed-wheel rehearsal

Editable installs prove development connectability. A release rehearsal must use built wheels in another clean environment.

From the repository root:

```bash
source .venv-codepotg-manual/Scripts/activate
python -m pip install build

for PACKAGE in \
  codepotg-v2 \
  codepotg-template-jinja \
  codepotg-language-typescript \
  codepotg-language-dart
do
  (
    cd "$REPO_ROOT/packages/python/$PACKAGE"
    rm -rf build dist
    python -m build
  )
done

py -3.12 -m venv .venv-codepotg-wheels
source .venv-codepotg-wheels/Scripts/activate
python -m pip install --upgrade pip
python -m pip install \
  "$REPO_ROOT/packages/python/codepotg-v2/dist/"*.whl \
  "$REPO_ROOT/packages/python/codepotg-template-jinja/dist/"*.whl \
  "$REPO_ROOT/packages/python/codepotg-language-typescript/dist/"*.whl \
  "$REPO_ROOT/packages/python/codepotg-language-dart/dist/"*.whl

cd "$REPO_ROOT/packages/python/codepotg-v2/examples/manual/connected-project"
rm -rf generated .codepotg
python verify_plugins.py
python bootstrap_contract.py
codepotg plan codepotg.yaml
codepotg generate codepotg.yaml
```

Repeat the TypeScript and Dart compiler checks. Only this phase proves installed distribution connectability.

## 17. Cleanup

Generated validation files are intentionally ignored by this guide, not automatically deleted:

```bash
rm -rf \
  generated \
  collision-output \
  .codepotg \
  plan.json \
  memory-output.json \
  write-report.json \
  rerun-report.json \
  before.sha256 \
  after.sha256 \
  contract.codepot.json \
  contract.codepot.yaml
```

## Human acceptance record

Record these results in the package audit before merging:

```text
[ ] correct branch and commit recorded
[ ] clean editable environment created
[ ] exact plugin graph loaded
[ ] JSON/YAML IR inspected and round-tripped
[ ] plan contained exactly 12 expected artifacts
[ ] memory render wrote nothing
[ ] managed generation wrote all expected files
[ ] deterministic rerun produced identical hashes
[ ] TypeScript compiler passed
[ ] Dart formatter/analyzer passed
[ ] edited managed file was protected
[ ] unchanged stale files were deleted
[ ] unmanaged collision was protected
[ ] codepotg-author gap reproduced
[ ] OpenAPI blocker reproduced
[ ] clean-wheel environment repeated the successful path
[ ] final git status recorded
```
