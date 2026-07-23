# Releasing CodepotG

This procedure publishes the first stable release as `codepotg==1.0.0`.

## Release status

The package is **not ready to upload** until `python scripts/release.py check` passes completely. The current release candidate uses `Codepotg.yaml`; the TypeScript workflow's `CodepotFile.yml` and `CodepotFile.yaml` names are intentionally rejected.

## PyPI account prerequisites

- The PyPI account email address must be verified.
- Two-factor authentication should be enabled.
- For the first upload of a project that does not yet exist, use an account-wide API token.
- After the project exists, revoke that token and create a token scoped only to `codepotg`.
- Store the token only in the ignored local `.env` file as `PUBLISH_TOKEN=...`.

Never commit `.env`, paste the token into a command, or include it in terminal screenshots.

## Prepare the release environment

From the repository root in Git Bash on Windows:

```bash
cd packages/python/codepotg
rm -rf .venv
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

On Linux or macOS, activate with `source .venv/bin/activate`.

## Validate the exact release

```bash
python scripts/release.py check
```

The checker performs tests, linting, build, Twine metadata validation, wheel and source-distribution inspection, clean-environment installation, and CLI smoke tests.

The expected files are:

```text
dist/codepotg-1.0.0-py3-none-any.whl
dist/codepotg-1.0.0.tar.gz
```

Do not publish when any check fails.

## Manual behavior gate

Before upload, create a clean temporary project and verify the public config workflow:

```bash
mkdir -p .release-smoke
cd .release-smoke
codepotg init --yes
cat Codepotg.yaml
```

Confirm the generated config is named `Codepotg.yaml`, contains no `templateDir` by default, and uses the bundled pack selected by `language`.

Then provide a valid OpenAPI document and run:

```bash
codepotg generate sdk --dry-run --verbose
```

Return to the package directory afterward:

```bash
cd ..
rm -rf .release-smoke
```

## Publish

Confirm `.env` exists without printing it:

```bash
test -s .env && echo "Local release environment exists"
```

Then run:

```bash
python scripts/release.py publish
```

The script reruns every release check before invoking Twine. It passes the token through `TWINE_PASSWORD`, uses `__token__` as the username, and never prints the credential.

## Verify from PyPI

Use a separate clean environment so the editable checkout cannot affect the result:

```bash
python -m venv .venv-pypi
source .venv-pypi/Scripts/activate
python -m pip install --upgrade pip
python -m pip install --no-cache-dir codepotg==1.0.0
codepotg --version
codepotg --help
python -m codepotg --version
```

Expected version output:

```text
codepotg 1.0.0
```

## Post-release token hardening

After the first upload:

1. open the PyPI project settings for `codepotg`;
2. create a new token scoped only to that project;
3. replace the local `PUBLISH_TOKEN` value;
4. revoke the account-wide bootstrap token.

## CodepotX OpenAPI compatibility gate

After PyPI installation is verified:

1. emit OpenAPI 3.0.3 or 3.1.0 from CodepotX;
2. point a `Codepotg.yaml` task at the emitted file;
3. run the debug template pack with `--dry-run --verbose`;
4. run one production template pack;
5. record unsupported schema or `x-codegen` shapes as CodepotX OpenAPI projection issues.

A PyPI release cannot be replaced. Any later correction must use a new version such as `1.0.1`.
