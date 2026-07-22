---
title: Publish to Open VSX
description: Publish Codepurify extension to Open VSX registry
---

# Publish to Open VSX

Publish the extension to the Open VSX registry for broader editor support.

## What is Open VSX?

Open VSX is a neutral extension registry:
- Alternative to Microsoft's marketplace
- Required for non-Microsoft editors
- Used by Windsurf, Cursor, and others

## Install CLI

```bash
npm install -g ovsx
```

## Publish Command

From the extension directory:

```bash
npx ovsx publish
```

## Namespace Requirement

Your extension needs a unique namespace:
- Set in `package.json` under `publisher`
- Must match your Open VSX account name

## Claim Namespace

1. Create account at [open-vsx.org](https://open-vsx.org)
2. Claim your publisher namespace
3. Verify ownership (usually via GitHub)

## Verification State

- **Unverified** - Works but shows warning
- **Verified** - Trusted status
- Verification improves discoverability

## Publishing Example

```bash
$ npx ovsx publish
Publisher: your-username
Extension name: codepurify
Version: 1.0.0

Successfully published!
```

## Post-Publishing

Extension becomes available at:
```
https://open-vsx.org/extension/your-username/codepurify
```

Users can now install via their editor's extension marketplace.
