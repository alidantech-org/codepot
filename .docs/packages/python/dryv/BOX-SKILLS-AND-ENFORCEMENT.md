# Dryv Box Skills and Enforcement

Status: research findings and architecture guidance. Not implemented and not part of the current canonical Dryv Runtime contract.

This document is a companion to [`BOX-ENGINEERING.md`](BOX-ENGINEERING.md). It records what Dryv can learn from the implemented DevAuto Skill system and from recent agent-harness/runtime-enforcement work.

The central finding is:

> A Box should define the finite implementation problem and the maximum authority available to solve it. Skills should supply reusable expertise inside that boundary. Skill rules may tighten the permitted process, but must never grant authority beyond the Box. Independent verification remains the final judge of whether the implementation is acceptable.

---

## 1. What was verified in DevAuto

The findings below come from the current `develop` branch of `alidantech-org/devauto`, especially:

- `devauto/agent/skills/activation/`;
- `devauto/agent/skills/composer/`;
- `devauto/agent/skills/discovery/`;
- `devauto/agent/skills/enforcement/`;
- `devauto/agent/skills/packages/`;
- `devauto/agent/skills/registry/`;
- `devauto/agent/tools/core/{activation,discovery,knowledge}.py`;
- `.catalog/skills/**`;
- `.docs/project/devauto/{RULES-SCHEMA,SKILL-MIGRATION}.md`.

The live Skill package format is YAML:

```text
skill/
├── skill.yaml
├── SKILL.md
└── rules.yaml       # optional
```

Some lower-level comments and the older schema document still say `rules.toml`, but the active package loader accepts `skill.yaml`, decodes `rules.yaml`, and the migration record says the TOML package format was removed. For design purposes the loading path is authoritative.

### `skill.yaml` — discovery and applicability

The manifest describes identity, discovery keywords, activation modes, priority/policy, capability requirements, dependencies/conflicts, and applicability to Tools/capabilities/effects.

This answers:

> When is this expertise relevant, required, available, or incompatible?

### `SKILL.md` — procedural expertise

The instruction document contains judgment, workflows, examples and engineering guidance that a model should reason about.

This answers:

> How should competent work of this kind be approached?

### `rules.yaml` — mechanically enforceable subset

The rules document contains only constraints that the harness can evaluate from structured execution facts.

The current closed rule vocabulary includes concepts equivalent to:

```text
deny_tool
allow_scope
require_capability
require_before
require_after
require_evidence
limit
require_state
```

The parser rejects unknown rule kinds/fields rather than allowing arbitrary executable policy expressions.

This answers:

> Which parts of the Skill can the harness objectively enforce?

These three responsibilities should remain separate in any Dryv adaptation.

---

## 2. DevAuto already implements progressive expertise loading

DevAuto exposes model-facing Skill discovery and activation operations:

```text
skills.discover
skills.describe
skills.activate
skills.deactivate
skills.active
```

Discovery returns compact metadata instead of loading every Skill instruction into context.

Activation validates dependencies, cycles, conflicts, allowed modes and required capabilities. It is all-or-nothing.

The full `SKILL.md` content enters model context only after activation, starting on the next model round. The composer also avoids resending unchanged Skill revisions already retained by the provider conversation.

This is directly useful for Box Engineering because a Box should not preload every possible project convention, framework guide, provider document and engineering workflow.

A better solver context is:

```text
Box goal
+ Box contract
+ required Skill summaries
+ searchable Skill catalog
+ searchable knowledge catalog
```

The solver can then discover and activate only the expertise relevant to the current obligation.

This is consistent with the broader progressive-disclosure pattern described by Anthropic Agent Skills: metadata first, full instructions when relevant, additional resources only when needed.

---

## 3. Enforcement is independent of model obedience

The most important DevAuto mechanism is not Skill prompting. It is the Skill enforcement gate.

Conceptually:

```text
model proposes Tool call
        ↓
Tool preparation / normalized effect
        ↓
required-Skill resolution
        ↓
active Skill rule evaluation
        ↓
Runtime policy
        ↓
actual effect
```

If a Tool/capability/effect requires a Skill that is not active, the action is blocked and the diagnostic identifies the missing Skill.

Active Skill rules are then evaluated against normalized Tool metadata and evidence.

The important authority rule in DevAuto is:

> Skill enforcement never grants authority. It only restricts activity that the Runtime already allows.

Dryv Box Engineering should adopt the same principle exactly.

---

## 4. Box authority and Skill authority must not be peers

A Box should define the capability ceiling.

For example:

```yaml
workspace:
  writable:
    - src/profile/**
  readonly:
    - generated/**

network:
  allow:
    - localhost:3000
```

An activated Skill may narrow that authority:

```text
Box write authority:
src/profile/**

Skill restriction:
src/profile/components/**

Effective authority:
src/profile/components/**
```

But the inverse must never happen:

```text
Box network authority:
none

Skill requests:
api.example.com

Effective authority:
none
```

The simplest policy algebra is:

```text
higher-authority permission
∩
lower-layer restrictions
=
effective permission
```

Never union.

A proposed precedence model is:

```text
organization/global policy
          ↓
project policy
          ↓
Box policy
          ↓
required Skill rules
          ↓
optional active Skill rules
          ↓
solver action
```

Lower layers may tighten a decision but must never weaken a higher layer.

---

## 5. Box, Skill, policy, capability and verifier are different concepts

The combined design is strongest when these remain first-class and separate.

| Concept | Question it answers |
| --- | --- |
| Box contract | What exactly must be implemented? |
| Skill | What reusable expertise should the solver know? |
| Policy/rules | What actions/process requirements are enforced? |
| Capabilities/sandbox | What can physically happen? |
| Verifier | Does the resulting implementation satisfy the obligation? |

A Skill must not become the Box.

A Box such as `CustomerProfilePage` can require a precise interface, writable files, states and acceptance gates. A reusable `project.interface-design` Skill can then teach design-system conventions, accessibility, responsive behavior and rendered verification.

The Box is the finite problem.

The Skill is reusable expertise.

---

## 6. Project guidance should be split by enforceability

Not every project rule belongs in a Skill rule file.

### Always-on project or Box policy

Examples:

```text
generated/** is read-only
only src/payments/stripe/** is writable
no new dependencies
network only to api.stripe.com
database unavailable
```

These must not depend on Skill activation.

### Required project Skills

Examples:

```text
project.frontend
project.payment-contracts
project.nestjs-conventions
```

These contain project-specific expertise that must be present for the relevant Box category.

### Discoverable optional Skills

Examples:

```text
accessibility.web
stripe.api
browser-debugging
react-performance
```

The solver may activate them when useful.

### Subjective guidance

Examples:

```text
match the existing visual hierarchy
avoid unnecessary abstractions
prefer the clearest interaction pattern
```

These usually belong in `SKILL.md`, a soft evaluator, or human review unless the harness has structured evidence sufficient to evaluate them deterministically.

---

## 7. Do not create fake hard rules

DevAuto contains an important negative example: some Skills intentionally have an effectively empty `rules.yaml` because their advice cannot be determined from Tool metadata alone.

For example, a harness can observe that a file was read. It cannot necessarily determine whether that read was unnecessary or whether a broad search was poor engineering judgment.

Dryv should preserve this discipline:

> A principle becomes a hard rule only when the harness has reliable structured evidence that can evaluate it.

Otherwise it remains instruction, evaluator guidance or human judgment.

This prevents the policy language from becoming an unreliable pseudo-formal system.

---

## 8. Required Skills and discovered Skills should coexist

The model should not choose whether mandatory project expertise applies.

A Box category may deterministically require Skills:

```yaml
skills:
  required:
    - project.frontend
    - project.design-system
```

The solver may then discover additional Skills:

```text
accessibility.web
forms.react
browser-debugging
```

This gives the system both safety and autonomy:

```text
mandatory knowledge is deterministic
optional expertise is discoverable
```

DevAuto already has the needed conceptual distinction through required versus recommended applicability.

---

## 9. Knowledge is not authority

DevAuto also separates durable Knowledge discovery from live Tool authority.

That distinction should be explicit in Box Engineering.

A Box solver may search:

```text
project architecture docs
existing implementation examples
design-system docs
provider API documentation
historical project knowledge
selected external sources
```

But retrieved content is only evidence for reasoning.

It must never:

- widen writable paths;
- grant network access;
- grant secrets;
- enable a Tool;
- replace mandatory policy;
- redefine Box acceptance.

The governing rule is:

> Knowledge may influence reasoning. Knowledge never grants authority.

This is also necessary for prompt-injection and supply-chain resistance.

---

## 10. External Skills require a trust model

A future Box solver may discover Skills outside the current project. Those Skills are supply-chain inputs and must not automatically receive the same trust as project-owned Skills.

A conservative first model is:

```text
Dryv core Skills       trusted
pack Skills            trusted according to pack trust
project Skills         trusted by project
user Skills            explicit user trust
external Skills        advisory by default
```

An untrusted/external Skill may provide knowledge or additional restrictions, but should not be able to:

- grant Tools;
- grant network destinations;
- grant secret access;
- widen writable scope;
- disable project/Box rules;
- redefine acceptance;
- silently execute bundled code.

Version and content hashes should be pinned for any Skill that materially affects a solve.

---

## 11. Three feedback loops should be distinguished

Combining Box verification with Skill enforcement gives the solver three useful feedback channels.

### Action-policy feedback

Before an effect:

```text
BLOCKED

Rule:
generated-files-read-only

Attempt:
write generated/api.ts
```

No forbidden action occurs.

### Process/evidence feedback

At completion:

```text
BLOCKED COMPLETION

Rule:
verify-rendered-ui

Missing:
browser observation after browser mutation
```

The solver knows what procedural evidence is missing.

### Implementation feedback

From the Box verifier:

```text
CONTRACT FAIL

Scenario:
provider returns HTTP 429

Expected:
PaymentTemporarilyUnavailable

Received:
ProviderHttpError
```

The candidate can then be repaired with minimal context.

These are different failures and should remain distinguishable in diagnostics and evidence.

---

## 12. Proposed combined architecture

```text
Canonical Dryv IR
        │
        ▼
Template Pack + Usage
        │
        ▼
deterministic Dryv planning
        │
        ├── Render Jobs
        │
        └── Implementation Obligation
                    │
                    ▼
                  BoxSpec
                    │
      ┌─────────────┼──────────────┐
      ▼             ▼              ▼
 Box Policy    Skill Catalog   Box Verifier
      │             │              │
      │        discover/activate    │
      │             │              │
      │         SKILL.md            │
      │             │              │
      └──────┬──────┘              │
             ▼                     │
        Solver Harness             │
             │                     │
       proposed action             │
             ▼                     │
        Policy Gate                │
        │         │                │
      block     allow              │
        │         │                │
        │       execute            │
        │         │                │
        └──── evidence ────────────┘
                  │
             completion gate
                  │
                  ▼
               verifier
              │       │
            fail     pass
              │       │
      counterexample accepted
              │
              └──────► solver repair
```

The solver remains replaceable. None of this requires Canonical IR to become AI-specific.

---

## 13. Where the responsibilities belong in Dryv

The existing Dryv architecture remains authoritative:

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating / deterministic planning
    ↓
Usage and generated output
```

The combined Skill/enforcement work must not move solver concerns into Canonical IR.

### Canonical Runtime IR

Owns software meaning only:

```text
inputs
outputs
errors
invariants
relationships
semantic contracts
```

It must not contain model names, prompts or Skill activation state.

### Packs

May help derive implementation obligations because packs know integration shape, generated interfaces, planned paths and required project bindings.

### Usage/project configuration

May supply project-level policy, approved Skill sources, project Skills, bindings and output/workspace decisions.

### Solver harness

Owns nondeterministic solving, Skill discovery/activation, Tool execution and enforcement integration.

It should remain outside the deterministic Runtime.

### Verifier

Evaluates the candidate independently and emits durable evidence/counterexamples.

---

## 14. Provenance should be part of Box evidence

An accepted implementation should eventually be explainable with identities/hashes similar to:

```yaml
box:
  id: profile-page
  spec_hash: ...

skills:
  - id: project.interface-design
    version: 3
    manifest_hash: ...
    instructions_hash: ...
    rules_hash: ...

knowledge:
  project_revision: ...

policy:
  hash: ...

candidate:
  hash: ...

verification:
  hash: ...
```

This allows Dryv to explain not merely that a solver produced code, but which Box, policies, Skills, knowledge revisions and verifier evidence were involved.

---

## 15. Example: UI Box

```text
BOX
CustomerProfilePage
```

Box contract:

```text
consume CustomerProfileViewModel
may call updateProfile() / uploadAvatar()
write src/features/profile/**
read generated/** but never modify it
support loading / loaded / validation-error / save-error
browser limited to project preview
```

Required Skill:

```text
project.interface-design
```

Discoverable Skills:

```text
accessibility.web
forms.react
browser-debugging
```

Enforcement:

```text
generated writes blocked
filesystem changes require verification
browser mutation requires rendered observation
```

Verifier:

```text
typecheck
build
component contract
interaction scenarios
accessibility baseline
viewport checks
```

Soft evaluation remains separate for visual hierarchy and aesthetic quality.

---

## 16. Example: external provider Box

```text
BOX
StripePaymentGateway
```

Box contract:

```text
implements PaymentGateway
write stripe-gateway.ts only
network api.stripe.com only
secret STRIPE_SECRET_KEY through bounded secret binding
database unavailable
generated contracts read-only
```

Required Skill:

```text
project.payment-contracts
```

Optional Skill:

```text
stripe.api
```

Knowledge:

```text
selected Stripe docs
project HTTP client
project error conventions
```

Verifier:

```text
success
401
429
500
timeout
malformed response
idempotency
currency mapping
```

The provider Skill may improve competence but cannot widen the Box network/secret/filesystem authority.

---

## 17. Research alignment

The DevAuto design is consistent with several external directions:

- OpenAI, **Harness engineering: leveraging Codex in an agent-first world** (2026): repository knowledge as a system of record, agent legibility, and mechanical enforcement of architecture/taste where possible.  
  https://openai.com/index/harness-engineering/

- Anthropic, **Agent Skills** documentation: modular domain expertise with progressive disclosure from metadata to instructions/resources.  
  https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview

- AgentSpec, **Customizable Runtime Enforcement for Safe and Reliable LLM Agents** (2025): structured runtime constraints around autonomous agent actions.  
  https://arxiv.org/abs/2503.18666

- VIGIL, **Runtime Enforcement of Behavioral Specifications in AI Agent Skills** (2026): enforcement over agent-tool traces, including temporal/cross-call constraints.  
  https://arxiv.org/abs/2606.26524

- Open Policy Agent: policy-decision versus policy-enforcement separation is a useful precedent for keeping rule evaluation distinct from effect execution.  
  https://www.openpolicyagent.org/docs/

- Model Context Protocol Tool specification: Tool execution should remain structured, permission-aware and return actionable errors that models can use for correction.  
  https://modelcontextprotocol.io/specification/

These sources support the direction, but Dryv should preserve its own architecture rather than copying any one agent framework.

---

## 18. Design recommendations

The current recommendation is:

1. Keep `BOX-ENGINEERING.md`'s fundamental model: a Box is a solver-neutral machine-readable implementation obligation.
2. Introduce Skills only at the solver-harness layer, not into Canonical IR.
3. Treat project/Box policy as always-on and higher authority than Skills.
4. Reuse the DevAuto separation of Skill metadata, procedural instructions and typed enforceable rules.
5. Support deterministically required Skills plus solver-discovered optional Skills.
6. Load Skill instructions progressively to preserve small context.
7. Make Skill rules restrictive only; never allow them to grant capabilities.
8. Keep Knowledge discovery independent from authority.
9. Add trust/provenance/versioning for project, pack, user and external Skills.
10. Do not encode subjective engineering judgment as hard policy unless the harness has reliable structured evidence.
11. Keep action-policy failures, completion/evidence failures and verifier failures distinct.
12. Preserve an independent Box verifier as the final acceptance authority.

---

## 19. What not to do

Do not evolve the system into:

```text
Box = giant prompt
Skill = another prompt fragment
rules.yaml = arbitrary expression language
model = policy judge
model = verifier
```

Do not allow:

```text
Skill grants network
Skill grants secret
Skill widens writable path
external docs alter authority
external Skill overrides project policy
solver declares itself complete without verifier evidence
```

That would recreate the same hidden-agent-magic problem Box Engineering is intended to remove.

---

## 20. Resulting principle

The combined architecture can be summarized as:

> Give the solver the smallest sufficient world in which the desired implementation is possible. Make relevant expertise progressively discoverable inside that world. Enforce the world's authority and objective process rules outside the model. Let an independent verifier decide whether the result satisfies the Box.

This produces a useful balance:

```text
small context
+
highly relevant expertise
+
solver autonomy inside the obligation
+
low authority outside the obligation
+
independent acceptance evidence
```

That is the part of the DevAuto Skill work worth carrying forward into Dryv Box Engineering.
