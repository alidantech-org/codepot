# codepot Templates

Universal templating language support for VS Code.

codepot adds syntax highlighting, autocomplete, diagnostics, and block validation for codepot template files embedded inside real programming languages.

Supports templates like:

- `entity.ts.codepot`
- `schema.sql.codepot`
- `widget.dart.code`
- `service.go.codepot`

## Syntax

Expressions:

```txt
{|entity.name.camel|}
```

Blocks:

```txt
{|if condition|}
...
{|else|}
...
{|/if|}
```

Loops:

```txt
{|loop field in entity.fields|}
  {|field.name.camel|}: {|field.type|}
{|/loop|}
```

Comments:

```txt
{|# comment #|}
```

Documentation comments:

```txt
{|* docs *|}
```

## Features

- Universal embedded template syntax
- Multi-language support
- Syntax highlighting
- Block validation
- Auto closing pairs
- Snippets and completions
- Comment and documentation blocks
- Host language coexistence

## Supported Languages

- TypeScript
- JavaScript
- TSX / JSX
- SQL
- Dart
- Go
- Rust
- Java
- Python
- C / C++
- C#
- PHP
- Ruby
- Kotlin
- Swift
- HTML / CSS / SCSS
- JSON / YAML
- Markdown
- Dockerfile
- Shell

## File Extensions

codepot supports:

- `.codepot`
- `.code`

Examples:

- `entity.ts.codepot`
- `entity.ts.code`
- `schema.sql.codepot`
- `widget.dart.code`

## Notes

codepot syntax is always prioritized inside `{| ... |}` regions while the host language continues to highlight the surrounding file normally.
