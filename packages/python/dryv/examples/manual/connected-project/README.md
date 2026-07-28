# Human validation: connected Dryv project

This is a real, inspectable project—not a pytest fixture. It lets a developer author semantic input three ways, run the same local packs, inspect plans and generated code, compile two target languages, deliberately break generated files, and verify safe recovery.

## What this workspace connects

```text
A. public dryv.ir Python objects
B. dryv-author -> public Contract -> core canonical codec
C. standard OpenAPI -> dryv-openapi -> public Contract
                         |
                         v
                 Dryv orchestrator
                         |
           +-------------+-------------+
           |                           |
   local TypeScript pack        local Dart pack
           |                           |
      sandboxed Jinja              sandboxed Jinja
           |                           |
 TypeScript target adapter       Dart target adapter
           |                           |
       tsc --noEmit             dart format/analyze
```

The three sources intentionally use the same pack manifests and templates. This proves that software meaning belongs to the neutral contract while emitted language/framework text belongs to packs.

## Important current boundary

`dryv-author` now compiles a public `Contract`. However, its package-local `dumps_json()` / `dumps_yaml()` envelope is separate from the core-owned canonical transport consumed by the built-in `ir` source adapter. The working bridge is therefore:

```text
Author.compile()
    -> result.contract
    -> dryv.ir.contract_to_json()
    -> adapter: ir
```

The manual author bootstrap follows that route deliberately. Treat the duplicate author-package codec as an integration defect until transport ownership is unified.

---

## 1. Check out the synchronized manual-audit branch

From Git Bash:

```bash
git fetch origin
git switch chatgpt/codepotx-restart-orchestrator
git pull --ff-only

git branch --show-current
git rev-parse HEAD
```

The branch contains the latest `chatgpt/codepotx-restart` package work plus this manual workspace. Record the exact SHA in your acceptance notes.

## 2. Create a clean editable environment with all six packages

```bash
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

rm -rf .venv-dryv-manual
py -3.12 -m venv .venv-dryv-manual
source .venv-dryv-manual/Scripts/activate

python -m pip install --upgrade pip
python -m pip install \
  -e "$REPO_ROOT/packages/python/dryv" \
  -e "$REPO_ROOT/packages/python/dryv-author" \
  -e "$REPO_ROOT/packages/python/dryv-openapi" \
  -e "$REPO_ROOT/packages/python/dryv-template-jinja" \
  -e "$REPO_ROOT/packages/python/dryv-language-typescript" \
  -e "$REPO_ROOT/packages/python/dryv-language-dart"

cd "$REPO_ROOT/packages/python/dryv/examples/manual/connected-project"
rm -rf runs collision-output
rm -f contract*.codepot.json contract*.codepot.yaml
```

## 3. Verify installed entry points and plugin loading

```bash
python verify_plugins.py
```

Expected plugin IDs, each exactly once:

```text
source adapters: ir, openapi
target adapters: typescript, dart
template engines: jinja
```

Failure here means package installation/distribution connectability is broken; do not continue by importing private factories manually.

---

# Route A — Direct public IR

## 4. Author the neutral contract directly

```bash
python bootstrap_contract.py
```

Expected files:

```text
contract.codepot.json
contract.codepot.yaml
```

The script performs core validation and exact JSON/YAML round trips before succeeding.

Inspect the human-readable transport:

```bash
sed -n '1,180p' contract.codepot.yaml
```

Confirm that it contains neutral schemas, fields, tags, guidance, names, IDs, and constraints—but no TypeScript, Dart, React, Flutter, NestJS, ORM, controller, widget, import, or output-directory semantics.

## 5. Plan, render in memory, and generate direct IR

```bash
dryv plan dryv.yaml | tee plan-direct.json
dryv generate dryv.yaml --memory | tee memory-output-direct.json

test ! -d runs/direct
dryv generate dryv.yaml --destination runs/direct | tee write-report-direct.json
find runs/direct -type f | sort
```

Expected direct-route artifact paths:

```text
runs/direct/typescript/package.json
runs/direct/typescript/tsconfig.json
runs/direct/typescript/src/models/user.ts
runs/direct/typescript/src/models/ticket.ts
runs/direct/typescript/src/enums/role.ts
runs/direct/typescript/src/index.ts
runs/direct/dart/pubspec.yaml
runs/direct/dart/analysis_options.yaml
runs/direct/dart/lib/models/user.dart
runs/direct/dart/lib/models/ticket.dart
runs/direct/dart/lib/enums/role.dart
runs/direct/dart/lib/manual_sdk.dart
```

The plan should contain exactly 12 artifacts for this route.

Inspect representative output and ownership state:

```bash
sed -n '1,200p' runs/direct/typescript/src/models/user.ts
sed -n '1,120p' runs/direct/typescript/src/index.ts
sed -n '1,200p' runs/direct/dart/lib/models/user.dart
sed -n '1,120p' runs/direct/dart/lib/manual_sdk.dart
sed -n '1,260p' runs/direct/.dryv/generation-state.json
```

Confirm:

- the banner option and `contractSource` binding are visible;
- the `domain:audited` tag activates only pack-authored comments;
- `readonly`, optional, and nullable facts are represented differently but correctly per target;
- every import/export statement comes from a template;
- module specifiers come from target-adapter planning facts.

---

# Route B — Typed Python authoring

## 6. Compile `dryv-author` declarations into public IR

```bash
python bootstrap_author_contract.py
```

Expected files:

```text
contract.author.codepot.json
contract.author.codepot.yaml
```

The script calls `Author.compile()`, prints diagnostics, then intentionally uses the **core codec** for the orchestrator-compatible transport.

Inspect it:

```bash
sed -n '1,180p' contract.author.codepot.yaml
```

## 7. Plan and generate the author-compiled contract

```bash
dryv plan dryv-author.yaml | tee plan-author.json
dryv generate dryv-author.yaml --memory | tee memory-output-author.json
dryv generate dryv-author.yaml --destination runs/author | tee write-report-author.json
find runs/author -type f | sort
```

Expected: the same 12 target paths as Route A, under `runs/author/`, with author-specific banner/source comments.

Human comparison:

```bash
diff -u \
  runs/direct/typescript/src/models/user.ts \
  runs/author/typescript/src/models/user.ts || true

diff -u \
  runs/direct/dart/lib/models/user.dart \
  runs/author/dart/lib/models/user.dart || true
```

Differences should be explainable by intentionally different source metadata/tags/banner—not hidden target behavior in the authoring compiler.

## 8. Record the duplicate author transport defect

This is an audit probe, not the supported bridge:

```bash
python - <<'PY'
from dryv_author import Author, dumps_json
from dryv_author import field

source = Author("Author Codec Probe")
source.schema("Message", {"text": field(str)})
result = source.compile()
assert result.contract is not None
print(dumps_json(result.contract)[:160])
PY
```

You should see the author-package envelope beginning with `format: dryv.ir` in its compact JSON representation. Do not configure that output as `adapter: ir`; the core adapter uses the core-owned transport contract.

---

# Route C — Standard OpenAPI

## 9. Inspect the supported OpenAPI source

```bash
sed -n '1,220p' openapi.yaml
```

The fixture deliberately stays inside the currently implemented standard subset: components, schemas, tags, one path operation, parameters, responses, and local references. It does not use security semantics or `x-codegen`.

## 10. Plan and generate from OpenAPI

```bash
dryv plan dryv-openapi.yaml | tee plan-openapi.json
dryv generate dryv-openapi.yaml --memory | tee memory-output-openapi.json
dryv generate dryv-openapi.yaml --destination runs/openapi | tee write-report-openapi.json
find runs/openapi -type f | sort
```

Do not hard-code the OpenAPI artifact count before inspecting the plan: the adapter may normalize operation-owned structural schemas in addition to the named component schemas. Every artifact must still have a clear semantic cause, safe path, target, and template.

Inspect diagnostics in all three JSON reports. Standard input should produce no error diagnostics.

---

# Real target-tool verification

## 11. Compile every generated TypeScript project

Run after all three routes generate:

```bash
for ROUTE in direct author openapi
do
  echo "== TypeScript: $ROUTE =="
  (
    cd "runs/$ROUTE/typescript"
    npm install
    npm run typecheck
  )
done
```

Acceptance: all three pass `tsc --noEmit` without editing generated source.

## 12. Format and analyze every generated Dart package

Requires Dart SDK 3.3+ on `PATH`.

```bash
for ROUTE in direct author openapi
do
  echo "== Dart: $ROUTE =="
  (
    cd "runs/$ROUTE/dart"
    dart pub get
    dart format --output=none --set-exit-if-changed lib
    dart analyze
  )
done
```

Acceptance: all three format and analyze without editing generated source. If the Dart SDK is unavailable, record the route as blocked—never as passed.

---

# Determinism and writer safety

## 13. Prove deterministic regeneration

Do this on the direct route before npm/Dart installs add external files, or hash only managed source files:

```bash
find runs/direct/typescript/src runs/direct/dart/lib -type f -print0 \
  | sort -z | xargs -0 sha256sum > before-direct.sha256

dryv generate dryv.yaml --destination runs/direct > rerun-report-direct.json

find runs/direct/typescript/src runs/direct/dart/lib -type f -print0 \
  | sort -z | xargs -0 sha256sum > after-direct.sha256

diff -u before-direct.sha256 after-direct.sha256
```

Expected: no differences.

## 14. Prove modified managed-file protection

```bash
cp runs/direct/typescript/src/models/user.ts /tmp/dryv-user.ts
printf '\n// HUMAN EDIT THAT MUST BE PROTECTED\n' \
  >> runs/direct/typescript/src/models/user.ts

set +e
dryv generate dryv.yaml --destination runs/direct
EDIT_EXIT=$?
set -e

echo "exit=$EDIT_EXIT"
tail -n 4 runs/direct/typescript/src/models/user.ts
```

Acceptance:

- exit is non-zero;
- the human edit remains present;
- no partial overwrite is committed.

Recover:

```bash
cp /tmp/dryv-user.ts runs/direct/typescript/src/models/user.ts
dryv generate dryv.yaml --destination runs/direct
```

## 15. Prove unchanged stale managed-file deletion

```bash
python bootstrap_contract.py --without-ticket
dryv generate dryv.yaml --destination runs/direct

test ! -f runs/direct/typescript/src/models/ticket.ts
test ! -f runs/direct/dart/lib/models/ticket.dart
```

Restore:

```bash
python bootstrap_contract.py
dryv generate dryv.yaml --destination runs/direct
```

## 16. Prove unmanaged collision protection

```bash
rm -rf collision-output
mkdir -p collision-output/typescript/src/models
printf 'UNMANAGED HUMAN FILE\n' > collision-output/typescript/src/models/user.ts

set +e
dryv generate dryv.yaml --destination collision-output
COLLISION_EXIT=$?
set -e

echo "exit=$COLLISION_EXIT"
cat collision-output/typescript/src/models/user.ts
```

Acceptance:

- exit is non-zero;
- the unmanaged file is unchanged;
- no surrounding partial generation is committed.

---

# Honest unsupported-feature probes

## 17. OpenAPI `x-codegen` and security boundaries

The current OpenAPI adapter intentionally diagnoses rather than implements typed `x-codegen` and security semantics. Test its public result directly:

```bash
python - <<'PY'
from dryv.api import CancellationToken
from dryv.ports import SourceAdapterRequest
from dryv_openapi import OpenApiSourceAdapter

value = b'''openapi: 3.0.3
info: {title: Boundary Probe, version: 1.0.0}
security: [{bearerAuth: []}]
paths: {}
components:
  securitySchemes:
    bearerAuth: {type: http, scheme: bearer}
x-codegen:
  version: "2"
  groups: {}
'''
result = OpenApiSourceAdapter().normalize(
    SourceAdapterRequest(source_id="boundary-probe", content=value),
    CancellationToken(),
)
print([item.code for item in result.diagnostics])
print("contract produced:", result.contract is not None)
PY
```

Acceptance: diagnostics truthfully identify unimplemented semantics. Do not interpret preserved raw source data as typed support.

## 18. Command and Git-pack fail-closed behavior

Project/pack commands and Git pack resolution are separate approval/locking lanes. Add either only in a temporary copied config and verify planning fails with an explicit diagnostic. They must never be silently ignored or executed during this workspace.

---

# Fresh-wheel rehearsal

## 19. Build all six packages

From the repository root in the editable environment:

```bash
source "$REPO_ROOT/.venv-dryv-manual/Scripts/activate"
python -m pip install build

for PACKAGE in \
  dryv \
  dryv-author \
  dryv-openapi \
  dryv-template-jinja \
  dryv-language-typescript \
  dryv-language-dart
do
  (
    cd "$REPO_ROOT/packages/python/$PACKAGE"
    rm -rf build dist
    python -m build
  )
done
```

## 20. Repeat from wheels only

```bash
cd "$REPO_ROOT"
rm -rf .venv-dryv-wheels
py -3.12 -m venv .venv-dryv-wheels
source .venv-dryv-wheels/Scripts/activate
python -m pip install --upgrade pip

python -m pip install \
  "$REPO_ROOT/packages/python/dryv/dist/"*.whl \
  "$REPO_ROOT/packages/python/dryv-author/dist/"*.whl \
  "$REPO_ROOT/packages/python/dryv-openapi/dist/"*.whl \
  "$REPO_ROOT/packages/python/dryv-template-jinja/dist/"*.whl \
  "$REPO_ROOT/packages/python/dryv-language-typescript/dist/"*.whl \
  "$REPO_ROOT/packages/python/dryv-language-dart/dist/"*.whl

cd "$REPO_ROOT/packages/python/dryv/examples/manual/connected-project"
rm -rf runs
python verify_plugins.py
python bootstrap_contract.py
python bootstrap_author_contract.py

dryv generate dryv.yaml --destination runs/direct
dryv generate dryv-author.yaml --destination runs/author
dryv generate dryv-openapi.yaml --destination runs/openapi
```

Repeat the TypeScript and Dart target-tool loops. This phase proves distribution connectability rather than source-tree convenience.

---

## Cleanup

```bash
rm -rf runs collision-output
rm -f \
  contract.codepot.json \
  contract.codepot.yaml \
  contract.author.codepot.json \
  contract.author.codepot.yaml \
  plan-*.json \
  memory-output-*.json \
  write-report-*.json \
  rerun-report-*.json \
  before-*.sha256 \
  after-*.sha256
```

## Human acceptance record

```text
[ ] exact branch and SHA recorded
[ ] six editable packages installed cleanly
[ ] ir/openapi/typescript/dart/jinja entry points loaded exactly once
[ ] direct IR JSON/YAML inspected and round-tripped
[ ] direct IR plan contained the expected 12 artifacts
[ ] direct IR memory render wrote nothing
[ ] direct IR managed generation wrote expected files
[ ] dryv-author compiled a public Contract
[ ] author Contract used the core canonical codec
[ ] author route planned and generated both targets
[ ] standard OpenAPI route normalized, planned, and generated
[ ] all three TypeScript projects passed tsc
[ ] all three Dart packages passed format/analyze, or SDK absence was recorded honestly
[ ] deterministic rerun hashes matched
[ ] edited managed file was protected
[ ] unchanged stale managed files were deleted
[ ] unmanaged collision was protected
[ ] author-package duplicate transport was recorded
[ ] OpenAPI unsupported semantics emitted truthful diagnostics
[ ] Git/command lanes failed closed when probed
[ ] all six wheels built
[ ] wheel-only environment repeated all three routes
[ ] final git status --short recorded and reviewed
```
