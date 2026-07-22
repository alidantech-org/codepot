# Codepurify

> Semantic metadata inference engine + template compiler for generating architecture artifacts from typed domain configs.

---

# What is Codepurify?

- semantic metadata DSL
- normalized manifest compiler
- inference engine
- template-driven code generator

You define **facts** about your domain.

Codepurify infers:

- query capabilities
- mutation semantics
- relation groups
- workflows
- validation groups
- reusable template contexts

Templates decide final architecture output.

---

# Core Philosophy

```txt id="8zfr52"
Configs define facts
        ↓
Inference engine derives semantics
        ↓
Normalized context is generated
        ↓
Codepurify templates render output
```

Codepurify does **not** hardcode:

- NestJS
- TypeORM
- FastAPI
- GraphQL
- React
- REST
- DTO patterns
- folder structures

All architecture styles are implemented through templates.

---

# Features

- Strongly typed TypeScript configs
- Semantic metadata inference
- Codepurify-based generation
- Framework agnostic
- Runtime metadata compilation
- Query/mutation capability inference
- Typed enum transitions/workflows
- Semantic validation rule AST
- Relation graph inference
- JSON-safe normalized manifests
- Extensible template ecosystem

---

# License

MIT
