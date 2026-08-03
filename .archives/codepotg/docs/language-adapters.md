# Universal Language Adapter Plan

CodepotG is designed to generate any deterministic text format from the same normalized OpenAPI contract. No programming language, schema language, query language, documentation format, configuration language, infrastructure format, build language, or domain-specific language is excluded.

The adapter registry is open-ended so newly created languages can be added without changing inference or breaking existing packs. The implementation queue below is committed scope. Its ordering controls engineering sequence only; it does not rank or exclude languages.

## Adapter boundary

Every adapter supplies:

```text
canonical language name
aliases
default template pack
name and reserved-word rules
type mapping
literal formatting
validation mapping
import or dependency planning
comment and documentation syntax
file and package conventions
framework profiles
formatter and post-generation actions
adapter tests
template-pack tests
```

Every adapter consumes the same normalized contract. It must not parse raw OpenAPI or add target-language rules to inference.

## Pack profiles

One language can have multiple packs:

```text
plain models
runtime validation
client SDK
server interfaces
framework integration
ORM or persistence
UI bindings
documentation
configuration
migration or schema output
```

Profiles share one adapter and can specialize imports, files, annotations, packages, and framework conventions.

## Universal implementation queue

### Web and JavaScript ecosystem

```text
JavaScript
ECMAScript modules
CommonJS
TypeScript
JSX
TSX
Node.js
Deno
Bun
Next.js
React
Vue
Nuxt
Svelte
SvelteKit
Angular
SolidJS
Qwik
Astro
Lit
Ember
Preact
Alpine.js
JSDoc
```

### Python ecosystem

```text
Python
Typed Python
Pydantic
Dataclasses
attrs
Django
Django REST Framework
FastAPI
Flask
SQLAlchemy
SQLModel
Marshmallow
httpx clients
requests clients
```

### JVM ecosystem

```text
Java
Kotlin
Scala
Groovy
Clojure
ClojureScript
JRuby
Jython
Java records
Jakarta Bean Validation
Jackson
Spring
Spring Boot
Micronaut
Quarkus
Vert.x
JAX-RS
Retrofit
Ktor
Android models
Gradle Kotlin DSL
Gradle Groovy DSL
Maven POM
```

### .NET ecosystem

```text
C#
F#
Visual Basic .NET
ASP.NET Core
Minimal APIs
Entity Framework Core
System.Text.Json
Newtonsoft.Json
FluentValidation
Refit
Blazor
MSBuild
```

### Native and systems languages

```text
C
C++
Objective-C
Objective-C++
Swift
Rust
Go
Zig
Nim
D
V
Crystal
Carbon
Cython
Assembly documentation and bindings
WebAssembly interface types
```

### Apple ecosystem

```text
Swift
Objective-C
Swift Codable
Swift macros
SwiftUI bindings
Combine clients
URLSession clients
Vapor
Package.swift
```

### Mobile and cross-platform

```text
Dart
Flutter
Kotlin Android
Java Android
Swift iOS
Objective-C iOS
React Native TypeScript
React Native JavaScript
Xamarin C#
.NET MAUI
Ionic TypeScript
Capacitor TypeScript
NativeScript TypeScript
```

### Functional languages

```text
Haskell
PureScript
Elm
OCaml
ReasonML
ReScript
Standard ML
F#
Clojure
ClojureScript
Elixir
Erlang
Gleam
Idris
Agda
Lean
Coq extraction interfaces
Scheme
Racket
Common Lisp
Emacs Lisp
Fennel
```

### Dynamic and scripting languages

```text
Ruby
PHP
Perl
Raku
Lua
Tcl
Smalltalk
Crystal
Groovy
Julia
R
MATLAB
Octave
Wolfram Language
VBScript
AutoHotkey
AppleScript
Google Apps Script
```

### Ruby ecosystem

```text
Ruby plain classes
Sorbet
RBS
dry-struct
dry-validation
Rails
ActiveModel
ActiveRecord
Faraday
HTTParty
RubyGems specifications
```

### PHP ecosystem

```text
PHP classes
PHP enums
PHP attributes
PHPDoc
Symfony
Laravel
Laminas
Doctrine
Symfony Validator
Guzzle
Composer packages
```

### BEAM ecosystem

```text
Elixir structs
Ecto schemas
Phoenix controllers
Phoenix contexts
Tesla clients
Erlang records
Erlang maps
OTP behaviors
Gleam types
Gleam clients
```

### Go ecosystem

```text
Go structs
encoding/json
validator tags
net/http clients
net/http handlers
Gin
Echo
Fiber
Chi
GORM
sqlc-oriented models
Go modules
```

### Rust ecosystem

```text
Rust structs
Serde
validator
Reqwest
Hyper
Axum
Actix Web
Rocket
Diesel
SeaORM
SQLx
Cargo manifests
WASM bindings
```

### C and C++ ecosystem

```text
C structs
C headers
C source serializers
C++ classes
C++ structs
C++17 and C++20 models
Boost.JSON
nlohmann/json
RapidJSON
Qt models
gRPC C++
CMake
Meson
Conan
vcpkg manifests
```

### Scientific and data languages

```text
R
Julia
MATLAB
Octave
Wolfram Language
SAS
SPSS syntax
Stata
NumPy typing
Pandas models
Apache Arrow schemas
Polars schemas
```

### Legacy and enterprise languages

```text
COBOL
PL/I
Fortran
Ada
Pascal
Object Pascal
Delphi
ABAP
RPG
Natural
JCL
Apex
PeopleCode
PowerBuilder
Visual Basic 6
FoxPro
```

### Logic, theorem, and rule languages

```text
Prolog
Datalog
Answer Set Programming
CLIPS
Drools DRL
Rego
Open Policy Agent policies
Lean
Coq
Agda
TLA+
Alloy
Z notation
B specification
```

### Smart-contract and blockchain languages

```text
Solidity
Vyper
Move
Cairo
Sway
Cadence
Michelson
LIGO
Plutus
Huff
Yul
ink! Rust
CosmWasm Rust
Substrate Rust
Clarity
Pact
Scilla
```

### Database and query languages

```text
ANSI SQL
PostgreSQL SQL
MySQL SQL
MariaDB SQL
SQLite SQL
SQL Server T-SQL
Oracle PL/SQL
Snowflake SQL
BigQuery SQL
Redshift SQL
ClickHouse SQL
DuckDB SQL
DB2 SQL
CockroachDB SQL
Cassandra CQL
Cypher
Gremlin
SPARQL
GraphQL SDL
GraphQL operations
OData metadata
DAX
MDX
Kusto Query Language
PromQL
LogQL
InfluxQL
Flux
HiveQL
Pig Latin
```

### Schema and interface languages

```text
OpenAPI JSON
OpenAPI YAML
JSON Schema
AsyncAPI
GraphQL SDL
Protocol Buffers
gRPC service definitions
Apache Avro
Apache Thrift
Smithy
RAML
API Blueprint
WSDL
XML Schema
Relax NG
Schematron
FlatBuffers
Cap'n Proto
MessagePack schemas
CloudEvents schemas
FHIR StructureDefinition
OData CSDL
```

### Serialization and data formats

```text
JSON
JSON5
JSON Lines
YAML
TOML
XML
CSV
TSV
INI
Properties files
EDN
Transit
BSON descriptions
MessagePack descriptions
CBOR descriptions
Ion schemas
Parquet metadata
Arrow schema JSON
```

### Documentation and publishing formats

```text
Markdown
CommonMark
GitHub Flavored Markdown
MDX
AsciiDoc
reStructuredText
HTML
XHTML
LaTeX
TeX
Typst
DocBook
DITA
Man pages
Texinfo
Javadoc
KDoc
Rustdoc
Go documentation
PHPDoc
RDoc
YARD
Sphinx
MkDocs
Docusaurus
OpenAPI reference pages
```

### Markup and styling languages

```text
HTML
CSS
Sass
SCSS
Less
Stylus
PostCSS
Tailwind configuration
SVG
MathML
XAML
QML
FXML
Handlebars
Mustache
Liquid
Nunjucks
Jinja
Twig
ERB
Haml
Slim
Pug
Razor
```

### Shell and command languages

```text
POSIX sh
Bash
Zsh
Fish
PowerShell
Windows Batch
Command Prompt scripts
Nushell
Xonsh
Make recipes
Justfiles
Taskfiles
```

### Infrastructure and operations formats

```text
Terraform HCL
OpenTofu HCL
Pulumi TypeScript
Pulumi JavaScript
Pulumi Python
Pulumi Go
Pulumi C#
AWS CloudFormation JSON
AWS CloudFormation YAML
AWS CDK TypeScript
AWS CDK JavaScript
AWS CDK Python
AWS CDK Java
AWS CDK C#
Azure Bicep
ARM templates
Google Deployment Manager
Kubernetes YAML
Kubernetes JSON
Helm templates
Kustomize
Dockerfile
Docker Compose
Podman Compose
Nomad HCL
Consul configuration
Vault policies
Ansible YAML
SaltStack
Chef Ruby
Puppet
CFEngine
Nix
Guix Scheme
Dhall
CUE
Jsonnet
Starlark
Earthly Earthfile
```

### CI, build, and package formats

```text
GitHub workflow YAML
Woodpecker CI YAML
Jenkinsfile Groovy
GitLab CI YAML
CircleCI YAML
Buildkite YAML
Azure Pipelines YAML
Bitbucket Pipelines YAML
Drone YAML
Tekton YAML
Argo Workflows YAML
Bazel BUILD
Bazel Starlark
Buck
CMake
Meson
Make
Ninja
Gradle
Maven
Ant
SBT
Cargo
Go modules
npm package.json
pnpm workspace
Yarn workspace
Composer
RubyGems
Python pyproject.toml
Poetry
Conda
NuGet
Swift Package Manager
CocoaPods
Carthage
```

### Editor, lint, and tooling formats

```text
EditorConfig
ESLint configuration
Prettier configuration
Biome configuration
Ruff configuration
Black configuration
mypy configuration
Pylint configuration
Clippy configuration
rustfmt configuration
gofmt integration
golangci-lint configuration
Stylelint configuration
Checkstyle
Spotless
Sonar configuration
VS Code settings
JetBrains project metadata descriptions
Language Server configuration
```

### API testing and client collection formats

```text
Postman collections
Insomnia collections
Bruno collections
HTTP files
REST Client files
curl scripts
HTTPie scripts
Karate DSL
Cypress API tests
Playwright API tests
k6 scripts
JMeter plans
Gatling Scala
Locust Python
Pact contracts
OpenAPI conformance manifests
```

### Observability and policy formats

```text
OpenTelemetry collector YAML
Prometheus configuration
Grafana dashboards
Loki configuration
Tempo configuration
Alertmanager rules
Prometheus rules
Datadog monitors
New Relic configuration
Elastic ingest pipelines
Logstash configuration
Fluent Bit configuration
Fluentd configuration
Rego
Kyverno policies
Gatekeeper constraints
SELinux policy documentation
AppArmor profiles
```

### Game and engine ecosystems

```text
C# Unity
Unity ScriptableObject models
C++ Unreal Engine
Unreal reflection types
GDScript
Godot resources
Lua game bindings
Roblox Luau
Haxe
GameMaker Language
Ren'Py
```

### Hardware and embedded languages

```text
Verilog
SystemVerilog
VHDL
Chisel Scala
SpinalHDL Scala
Bluespec
Arduino C++
Embedded C
MicroPython
CircuitPython
Zephyr devicetree
Device Tree Source
PlatformIO configuration
```

### Domain-specific and generated artifacts

```text
regular expressions
finite-state-machine definitions
parser grammars
ANTLR grammars
Tree-sitter grammars
PEG grammars
OpenAPI gateway mappings
route manifests
permission manifests
cache manifests
entity diagrams
Mermaid
PlantUML
Graphviz DOT
BPMN
DMN
statecharts
localization catalogs
gettext PO
Android resources
iOS strings
```

## Ordering rules

Adapters are implemented in deterministic batches while every entry remains committed scope:

1. establish the universal adapter test kit and normalized contract;
2. complete existing TypeScript, Next.js, Dart, and debug adapters;
3. implement general-purpose language adapters and their standard-library profiles;
4. implement framework profiles for each language;
5. implement schema, query, documentation, configuration, infrastructure, build, policy, and domain-specific formats;
6. continuously add newly created languages to the same registry and test contract.

No adapter may require a breaking change to the normalized API contract. When a target needs additional information, the language-neutral contract is extended additively and every existing adapter remains valid.

## Adapter completeness

An adapter is complete when it has:

```text
registered canonical name and aliases
name and reserved-word tests
primitive and composed type mapping
nullable and optional mapping
default and literal mapping
validation mapping
reference and recursion handling
import planning
file naming
documentation syntax
representative template pack
snapshot tests
real-contract generation test
formatter or validation command where available
```

## Universal guarantee

The language registry never closes. Every deterministic textual language or format is eligible for an adapter, uses the same normalized source contract, and follows the same compatibility and testing requirements.
