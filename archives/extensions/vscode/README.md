# Codepurify Templates

Universal templating language support for VS Code.

Codepurify adds syntax highlighting, autocomplete, diagnostics, and block validation for Codepurify template files embedded inside real programming languages.

Supports templates like:

* `entity.ts.codepurify`
* `schema.sql.codepurify`
* `widget.dart.code`
* `service.go.codepurify`

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

* Universal embedded template syntax
* Multi-language support
* Syntax highlighting
* Block validation
* Auto closing pairs
* Snippets and completions
* Comment and documentation blocks
* Host language coexistence

## Supported Languages

* TypeScript
* JavaScript
* TSX / JSX
* SQL
* Dart
* Go
* Rust
* Java
* Python
* C / C++
* C#
* PHP
* Ruby
* Kotlin
* Swift
* HTML / CSS / SCSS
* JSON / YAML
* Markdown
* Dockerfile
* Shell

## File Extensions

Codepurify supports:

* `.codepurify`
* `.code`

Examples:

* `entity.ts.codepurify`
* `entity.ts.code`
* `schema.sql.codepurify`
* `widget.dart.code`

## Notes

Codepurify syntax is always prioritized inside `{| ... |}` regions while the host language continues to highlight the surrounding file normally.
