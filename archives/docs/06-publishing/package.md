---
title: Package Extension
description: Build and package the Codepurify extension for distribution
---

# Package Extension

Package the extension into a distributable `.vsix` file.

## Install Tooling

```bash
npm install -g vsce
```

## Package Command

From the extension directory:

```bash
vsce package
```

## What is a VSIX File?

A `.vsix` file is a Visual Studio Code extension package containing:
- Extension manifest (`package.json`)
- Compiled JavaScript code
- Assets and resources
- Extension metadata

## Result

The command creates a `.vsix` file:

```
codepurify-1.0.0.vsix
```

## Versioning

Update version in `package.json` before packaging:

```json
{
  "version": "1.0.0",
  "name": "codepurify"
}
```

## Output Example

```bash
$ vsce package
Executing prepublish script 'npm run compile'...

DONE  Packaged: codepurify-1.0.0.vsix (12.3 KB)
```

The `.vsix` file is ready for distribution via VSIX installation or Open VSX publishing.
