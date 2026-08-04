# Research sources

**Research completed:** 2026-08-02  
**Repository branch:** `chatgpt/develop`

This bibliography separates Codepot repository evidence from external evidence. External sources were selected primarily from official project documentation, original research organizations, and peer-reviewed or primary research publications.

## Repository evidence

### Active architecture and package family

- [Root Codepot README](../README.md) — ecosystem history, supported prototypes, CodepotX direction, and project principles.
- [Dryv README](../packages/python/dryv/README.md) — runtime-first API, package family, plugin graph, managed generation, and design principles.
- [Dryv design documentation index](../packages/python/dryv/docs/README.md) — normative reading order and superseded vocabulary warning.
- [Approved Dryv architecture](../packages/python/dryv/docs/00-governance/00-approved-architecture.md) — highest-priority design contract.
- [Closed semantic kernel](../packages/python/dryv/docs/00-governance/04-closed-semantic-kernel.md) — canonical topology, facets, selectors, contexts, dependencies, and growth rules.
- [Generation design index](../packages/python/dryv/docs/03-generation/README.md) — complete planning, fixed selectors, paths, and output safety.
- [Plugin design index](../packages/python/dryv/docs/04-plugins/README.md) — bounded plugin authority and package boundaries.
- [Distribution design index](../packages/python/dryv/docs/05-distribution/README.md) — package topology, direct Git packs, locking, and runtime interfaces.
- [Dryv progress log](../packages/python/dryv/docs/tasks/PROGRESS.md) — verified pre-rebrand baseline and post-rebrand verification status.
- [dryv-author README](../packages/python/dryv-author/README.md) — authoring responsibility boundary.
- [Approved Python authoring idea](../packages/python/dryv-author/docs/IDEA.md) — typed references, compilation pipeline, derivation, views, workflows, guidance, and transport boundary.

### Historical and transitional evidence

- [codepot-openapi README](../packages/nodejs/codepot-openapi/README.md) — original typed OpenAPI-centered authoring prototype.
- [Archived CodepotG README](../archives/codepotg/README.md) — mature OpenAPI-to-Jinja generator, lifecycle safety, JSONL, pack graph, and real-generation behavior.
- [CodepotX README](../packages/nodejs/codepotx/README.md) — JavaScript runtime rewrite, stable artifacts, platform adapters, and frontend-neutral runtime.
- Git history on `chatgpt/develop`, especially the June 2026 CodepotX work and July 2026 CodepotG v2/Dryv rebrand, runtime/CLI extraction, authoring design, and architecture tests.

## External evidence

The labels `[R1]` through `[R15]` are used by [`engineering-paper.md`](engineering-paper.md).

### Platform engineering and AI-assisted delivery

**[R1] DORA — Platform engineering**  
Google Cloud DORA. “Capabilities: Platform engineering.” Updated 2026-01-12.  
https://dora.dev/capabilities/platform-engineering/  
Relevant evidence: internal developer platforms, dedicated platform teams, golden paths, feedback quality, AI as an amplifier, and downstream disorder.

**[R2] DORA — 2025 State of AI-assisted Software Development**  
Google Cloud DORA. 2025 research and report materials.  
https://dora.dev/dora-report-2025/  
Relevant evidence: AI adoption interacts with organizational and delivery-system quality rather than producing uniform outcomes.

### Specification-driven AI development

**[R3] GitHub — Spec-driven development with AI**  
GitHub Blog. “Spec-driven development with AI: Get started with a new open source toolkit.” 2025-09-02.  
https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/  
Relevant evidence: living specifications as shared sources of truth and the limitations of one-shot vibe coding for serious systems.

### Platform templates and golden paths

**[R4] Backstage — Software Templates**  
Backstage official documentation.  
https://backstage.io/docs/features/software-templates/  
Relevant evidence: skeleton loading, variable collection, review, templated steps, repository publishing, and organizational scaffolding.

### Schema compatibility and governance

**[R5] Buf — Detecting breaking changes**  
Buf official documentation.  
https://buf.build/docs/breaking/  
Relevant evidence: deterministic comparison with prior schema state, policy categories, local/review/registry enforcement, and informed human decisions.

**[R6] Buf — Breaking-change usage guide**  
Buf official documentation.  
https://buf.build/docs/breaking/usage/  
Relevant evidence: custom option semantics are not automatically covered because arbitrary options have unbounded meanings.

### Established code generation

**[R7] OpenAPI Generator — official documentation and generator catalog**  
https://openapi-generator.tech/  
https://openapi-generator.tech/docs/generators/  
Relevant evidence: broad client, server, documentation, and schema generation from OpenAPI contracts.

### Semantic models and generator architecture

**[R8] Smithy — Creating a Code Generator**  
Smithy 2.0 official documentation.  
https://smithy.io/2.0/guides/building-codegen/index.html  
Relevant evidence: target-language-neutral service models and separation between generic and provider-specific code generation.

**[R9] Smithy — The model and code generation concepts**  
https://smithy.io/2.0/spec/model.html  
https://smithy.io/2.0/guides/building-codegen/implementing-the-generator.html  
https://smithy.io/2.0/guides/building-codegen/decoupling-codegen-with-symbols.html  
Relevant evidence: semantic models, directed codegen, symbol planning, dependency handling, and reusable generator structures.

### Developer trust and AI-agent concerns

**[R10] Stack Overflow — 2025 Developer Survey, AI section**  
https://survey.stackoverflow.co/2025/ai  
Relevant evidence: AI adoption, distrust of output accuracy, almost-correct solutions, debugging cost, resistance to high-responsibility tasks, agent accuracy/security concerns, and limited collaboration impact.

### AI productivity measurement

**[R11] METR — Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity**  
METR, 2025-07-10.  
https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/  
Paper: https://metr.org/Early_2025_AI_Experienced_OS_Devs_Study-paper.pdf  
Relevant evidence: randomized study of experienced developers on familiar repositories and observed 19% slowdown under the studied early-2025 conditions.

**[R12] METR — We are Changing our Developer Productivity Experiment Design**  
METR, 2026-02-24.  
https://metr.org/blog/2026-02-24-uplift-update/  
Relevant evidence: newer tools may offer more benefit, but selection effects and measurement issues complicate updated estimates.

### Model-driven and domain-specific engineering

**[R13] Give me some REST: A Controlled Experiment to Study Effects and Perception of Model-Driven Engineering with a Domain-Specific Language**  
ACM/IEEE MODELS 2024.  
https://doi.org/10.1145/3640310.3674080  
Relevant evidence: controlled evaluation of both effects and developer perception for a REST-oriented DSL.

**[R14] Domain-specific languages in practice: A user study on the success factors**  
Hermans, Pinzger, and Van Deursen. MODELS 2009.  
https://doi.org/10.1007/978-3-642-04425-0_33  
Relevant evidence: industrial DSL use, maintainability and reuse benefits, and conditional success factors.

**[R15] A Survey on LLM-based Code Generation for Low-Resource and Domain-Specific Programming Languages**  
2024 survey preprint.  
https://arxiv.org/abs/2410.03981  
Relevant evidence: data scarcity, specialized syntax, evaluation limitations, and lack of standardized benchmarks for low-resource and domain-specific languages.

## Additional useful references

### Buf governance

- Rules and categories: https://buf.build/docs/breaking/rules/
- Schema checks: https://buf.build/docs/bsr/checks/
- Buf images: https://buf.build/docs/reference/images

### Backstage templates

- Adding templates: https://backstage.io/docs/features/software-templates/adding-templates/
- Writing templates: https://backstage.io/docs/features/software-templates/writing-templates/
- Software Catalog system model: https://backstage.io/docs/features/software-catalog/system-model/

### Smithy code generation

- Overview and concepts: https://smithy.io/2.0/guides/building-codegen/overview-and-concepts.html
- Using the semantic model: https://smithy.io/2.0/guides/building-codegen/using-the-semantic-model.html
- Making codegen pluggable: https://smithy.io/2.0/guides/building-codegen/making-codegen-pluggable.html

### OpenAPI Generator

- Creating a generator: https://openapi-generator.tech/docs/new-generator/
- CLI usage: https://openapi-generator.tech/docs/usage/
- Integrations: https://openapi-generator.tech/docs/integrations/

### Industrial DSL engineering

- “Towards a Systematic Engineering of Industrial Domain-Specific Language.” 2021.  
https://arxiv.org/abs/2103.09682

## Interpretation cautions

1. Survey percentages describe the surveyed population, not every developer or organization.
2. The METR early-2025 result is specific to its participants, repositories, tasks, and tools; the 2026 update explicitly discusses changed conditions and selection effects.
3. Mature adjacent tools prove demand for focused capabilities, not demand for Codepot’s complete scope.
4. Model-driven engineering research shows conditional benefits and recurring adoption barriers; it does not guarantee that a new semantic platform will succeed.
5. Repository design documents establish intent and contracts. They do not prove production effectiveness unless paired with exact-head verification and real-project evidence.

## Source maintenance rule

When these documents are updated:

- record the review date;
- prefer official or primary sources;
- preserve contrary or limiting evidence;
- distinguish current facts from historical facts;
- update public claims only when Codepot-specific evidence advances.
