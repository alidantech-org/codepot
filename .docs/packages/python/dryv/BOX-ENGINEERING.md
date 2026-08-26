# Dryv Box Engineering

Status: research-backed architecture proposal. Not implemented and not part of the current canonical Runtime contract.

## Purpose

Dryv is designed to generate software deterministically from a canonical description of software meaning. That works well when a template pack can completely describe how Runtime IR becomes generated output.

Some software cannot or should not be template-generated completely:

- a custom business algorithm;
- a project-specific external API integration;
- a UI whose visual composition requires design judgment;
- an adapter for a vendor that Dryv does not understand;
- a transformation whose implementation is unique to one project;
- glue code whose shape is known but whose exact behavior must be authored;
- code that requires exploration rather than deterministic rendering.

The usual response is to generate a stub, a TODO, or a broad extension point and leave a human or AI agent to inspect the surrounding repository and implement it.

That throws away much of the information Dryv already has.

If the software contracts, generated interfaces, dependencies, permitted effects, expected behavior, and output conventions are already known, Dryv can use that information to create a bounded implementation problem rather than an unstructured TODO.

This document calls that problem an **Implementation Box** and calls the wider engineering approach **Box Engineering**.

The central idea is:

> Dryv deterministically creates a bounded implementation obligation whose interfaces, relevant context, writable surface, capabilities, constraints, and definition of done are machine-readable. A human or AI solver may implement the missing code inside that boundary. Independent verification determines whether the implementation is acceptable.

The important property is that the solver does not own the architecture.

The architecture remains outside the box.

---

## Core model

```text
software meaning
      ↓
Canonical Dryv Runtime IR
      ↓
pack selection and planning
      ↓
┌───────────────────────────────────────┐
│ deterministic generated artifacts    │
└───────────────────────────────────────┘
      +
┌───────────────────────────────────────┐
│ bounded implementation obligations   │
│                                       │
│  interface                            │
│  context                              │
│  capabilities                         │
│  writable surface                     │
│  constraints                          │
│  acceptance                           │
│  verification                         │
└───────────────────────────────────────┘
                  ↓
          human or AI solver
                  ↓
          candidate implementation
                  ↓
          independent verifier
             ↓             ↓
           fail           pass
             ↓             ↓
      counterexample    accepted
             ↓
           repair
```

The solver is intentionally replaceable. It may be:

- a developer;
- Codex;
- Claude;
- Gemini;
- a local model;
- a specialized coding agent;
- a future program synthesizer;
- another automated implementation system.

Dryv should not require an AI model in order for a Box to be useful.

A Box is therefore better understood as a **machine-readable implementation contract** than as an AI prompt.

---

## Why this matters for Dryv

Dryv currently separates responsibilities deliberately:

```text
Authoring
    ↓
Canonical Dryv Runtime IR
    ↓
Templating
    ↓
Usage and generated output
```

Box Engineering should preserve that separation.

It extends the usefulness of deterministic generation without pretending that every source file can be rendered from a template.

A useful long-term goal is not necessarily:

> Dryv generates 100% of application source code.

A stronger and more achievable goal may be:

> Dryv generates everything that can be generated deterministically and creates an explicit, bounded, verifiable obligation for everything that still requires implementation.

That would let Dryv describe the architecture of generated and custom code using the same contracts while preserving a clear distinction between deterministic output and authored or synthesized implementation.

---

## Relationship to existing engineering ideas

Box Engineering is not based on the assumption that AI agents need unlimited repository context. Several established research directions suggest the opposite: software synthesis improves when the implementation space, interfaces, feedback, and evaluation criteria are explicit.

### Program synthesis and CEGIS

Counterexample-Guided Inductive Synthesis, or CEGIS, uses a loop roughly like:

```text
candidate
   ↓
verifier
   ↓
fail with counterexample
   ↓
new candidate
   ↓
verifier
```

The important lesson for Dryv is that the implementation system should not be the final judge of its own work.

A Box verifier should return concrete evidence such as:

```text
TYPE_GATE       PASS
COMPILE_GATE    PASS
CONTRACT_GATE   FAIL

Scenario:
provider returned HTTP 429

Expected:
CarrierUnavailable(retryAfter=30)

Received:
UnhandledHttpException
```

The next solver iteration can then operate with a very small context:

```text
goal
+ contract
+ current implementation
+ latest counterexample
```

This is much more useful than asking a model to repeatedly reread an entire repository.

Relevant background:

- SKETCH and program synthesis: https://people.csail.mit.edu/asolar/
- Syntax-Guided Synthesis: https://sygus.org/
- CEGIS background in synthesis literature: https://www.microsoft.com/en-us/research/research-area/programming-languages-methods/

### Component interfaces

The WebAssembly Component Model and WIT demonstrate a related architectural principle: a component can declare what it imports and exports without defining how its implementation is written.

That provides a strong precedent for a language-agnostic boundary of the form:

```text
these capabilities are available
these interfaces must be implemented
```

Relevant background:

- WebAssembly Component Model: https://component-model.bytecodealliance.org/
- WIT: https://component-model.bytecodealliance.org/design/wit.html

### Coding-agent interfaces and harnesses

Modern coding-agent work has repeatedly shown that the environment around the model matters as much as the prompt. Agent-computer interfaces, bounded tools, explicit tests, repository instructions, evaluator separation, and structured state all improve the probability that an agent can make reliable progress.

Relevant background:

- SWE-agent: https://swe-agent.com/
- OpenAI, Harness engineering: https://openai.com/index/harness-engineering/
- Anthropic, effective harnesses for long-running agents: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

Box Engineering takes this idea one step closer to the software architecture itself: wherever possible, the harness should be **derived from declared software contracts and generation planning**, not reconstructed later from repository conventions.

---

## Box Engineering versus Graph Engineering

Graph Engineering and Box Engineering solve different problems.

A graph answers questions such as:

- which task depends on which other task;
- which agent performs each task;
- which work can run in parallel;
- when a reviewer or evaluator should run;
- how state moves across a larger goal.

A Box answers:

- what exactly must this implementation do;
- what may it consume;
- what must it produce;
- what capabilities may it use;
- what files may it change;
- what behavior is forbidden;
- how completion is verified.

Conceptually:

```text
Graph Engineering
answers:
WHO does WHAT and WHEN?

Box Engineering
answers:
WHAT IS THIS IMPLEMENTATION ALLOWED TO DO,
WHAT MUST IT PRODUCE,
AND WHAT COUNTS AS PROOF OF COMPLETION?
```

The two ideas can compose naturally.

A future task graph can contain Boxes as independently verifiable nodes:

```text
                 project goal
                      │
              ┌───────┴───────┐
              ▼               ▼
         ┌─────────┐      ┌─────────┐
         │ BOX A   │      │ BOX B   │
         │ backend │      │   UI    │
         └────┬────┘      └────┬────┘
              │                 │
              └────────┬────────┘
                       ▼
                  ┌─────────┐
                  │ BOX C   │
                  │integrate│
                  └─────────┘
```

Dryv does not need a graph orchestrator in order to make individual Boxes useful.

---

## Architectural boundary

Box Engineering must not weaken the existing Dryv architecture.

### Runtime IR remains the only semantic authority

Canonical Runtime IR must continue to represent software meaning.

Runtime IR should not acquire model-specific fields such as:

```yaml
ai: true
model: gpt
prompt: implement this
```

Those fields describe an implementation mechanism, not software meaning.

The canonical relationship should remain:

```text
Canonical IR
    = software meaning

Pack
    = generation and implementation mapping

Implementation Box
    = bounded implementation obligation derived from
      canonical meaning + pack meaning + usage bindings
```

A Box must never become a competing semantic model.

### Authoring does not become AI authoring

Authoring implementations continue to:

- define software meaning;
- validate authored definitions;
- compile into Canonical Runtime IR.

They must not:

- choose AI models;
- define prompts;
- manage solver execution;
- create generated files;
- directly create Box workspaces.

If authoring gains richer behavioral contracts in the future, those contracts are justified because they describe software meaning, not because an AI requires them.

### Runtime planning remains deterministic

The Dryv Runtime currently stops at `GenerationPlan`.

That property should remain true.

If Box support becomes real, Runtime may eventually plan implementation obligations in the same deterministic sense that it plans render work, but it must not execute an AI solver.

Conceptually:

```text
RuntimeInput
    ↓
Dryv Runtime
    ↓
GenerationPlan
    ├── deterministic render jobs
    └── deterministic implementation obligations
```

Whether implementation obligations belong directly in `GenerationPlan`, in a related plan section, or in a separate derived plan is an implementation decision that must be designed carefully before code changes are made.

The key rule is fixed:

> Runtime may describe the obligation. Runtime does not synthesize the implementation.

### Solver execution is nondeterministic and separate

A future interface might look conceptually like:

```text
dryv build
```

for deterministic generation planning and rendering, and separately:

```text
dryv box inspect carrier-quote
dryv box verify carrier-quote
dryv box solve carrier-quote
```

The exact CLI is not approved here.

The architectural separation is:

```text
deterministic planning
        ↓
implementation obligation
        ↓
nondeterministic solver
        ↓
candidate implementation
        ↓
deterministic verification where possible
```

This avoids making model output part of Dryv's deterministic generation guarantee.

---

## First-class Box concepts

A practical implementation will probably need concepts close to the following. These names are proposals, not approved API names.

### `BoxSpec`

The complete machine-readable implementation obligation.

It answers:

- what is the goal;
- which semantic subject created the obligation;
- which interface must be implemented;
- which inputs and outputs are relevant;
- which constraints apply;
- which effects are allowed;
- what acceptance gates exist.

### `BoxContext`

The minimal information necessary to solve the obligation.

Possible contents include:

- relevant generated interfaces;
- relevant canonical types;
- selected documentation excerpts;
- fixtures;
- examples;
- dependency interfaces;
- design tokens;
- provider protocol information;
- the current candidate implementation;
- latest verifier failures.

The goal is not to maximize context. The goal is to make the smallest sufficient context deterministic and explainable.

### `BoxWorkspace`

The exact writable surface of the obligation.

It can define:

- files the solver owns;
- directories it may create within;
- generated files that are read-only;
- files available only as context;
- paths explicitly forbidden from modification.

### `BoxCapabilities`

The capabilities available to the implementation and/or solver.

Examples:

- HTTP access to a specific provider;
- a generated logger interface;
- one configuration value;
- one secret binding;
- filesystem access to a bounded temporary directory;
- no database access;
- no shell access;
- no network except declared hosts.

This makes the software dependency boundary useful as an agent security boundary as well.

### `BoxVerifier`

An independent mechanism for evaluating a candidate.

Possible gates include:

- syntax;
- type checking;
- compilation;
- contract scenarios;
- property checks;
- state-transition checks;
- snapshot or structural output validation;
- accessibility checks;
- allowed dependency checks;
- filesystem mutation checks;
- network policy checks;
- deterministic behavior checks;
- human review;
- a separate AI evaluator for subjective quality.

### `BoxEvidence`

The durable record explaining why a particular implementation was accepted.

Conceptually:

```yaml
box: carrier-quote
specHash: 8e21...
contractHash: ac72...
packVersion: 2.3.0
implementationHash: 0f19...

verification:
  types: passed
  contracts: passed
  policies: passed
```

This evidence should not claim mathematical proof unless the verifier actually provides it.

---

## A conceptual Box contract

The exact serialization is not designed yet. A future representation might carry information equivalent to:

```yaml
id: carrier-quote

subject:
  kind: operation
  ref: shipping.calculateQuote

goal: >
  Implement the carrier quotation adapter.

implements:
  interface: CarrierQuoteProvider
  member: quote

inputs:
  - Shipment

outputs:
  - DeliveryQuote

errors:
  - CarrierUnavailable
  - UnsupportedDestination

context:
  interfaces:
    - generated/contracts/shipping.ts
  fixtures:
    - fixtures/carrier/*.json

workspace:
  writable:
    - src/integrations/carrier/quote.ts
  readonly:
    - generated/**
    - src/contracts/**

capabilities:
  network:
    allow:
      - api.carrier.example
  secrets:
    - CARRIER_API_KEY
  filesystem: none
  database: none

acceptance:
  - typecheck
  - compile
  - contract-scenarios
  - network-policy
```

This is deliberately more structured than a prompt.

A solver-specific adapter may turn this contract into an effective prompt or tool environment, but the Box itself should remain solver-neutral.

---

## Example: external API integration

External API adapters are one of the strongest initial use cases.

Suppose the canonical software model describes:

```text
Calculate delivery quote

input:
Shipment

output:
DeliveryQuote

errors:
CarrierUnavailable
UnsupportedDestination
```

A pack can generate the application-facing interface and all code that consumes it, while leaving the provider-specific implementation unresolved.

The generated architecture becomes:

```text
Generated application
        │
        ▼
CarrierQuoteProvider
        │
   ┌────┴─────┐
   │   BOX    │
   └────┬─────┘
        │
        ▼
External carrier API
```

The Box may expose provider fixtures such as:

```text
success
401
404
429
500
timeout
malformed payload
unsupported destination
network disconnect
```

The implementation must map them into the already-declared application contract.

The solver does not need to understand unrelated application domains, controllers, database tables, or generated files.

It only needs enough information to satisfy the adapter contract.

---

## Example: custom business function

Consider a pricing rule that cannot be expressed safely as a generic template.

Dryv may know:

```text
input:
BookingPricingContext

output:
PriceBreakdown

invariants:
final price must never be negative
currency must be preserved
base price must be represented in the result

forbidden effects:
network
database
filesystem
```

The Box can then give a solver only:

```text
PricingPolicy interface
BookingPricingContext type
PriceBreakdown type
examples
property checks
owned source file
```

This kind of Box could be extremely reliable because the environment is small and the verifier can be strong.

---

## Example: UI implementation

UI generation is harder because visual quality is partly subjective, but the Box can still constrain integration strongly.

A `CustomerProfilePage` Box might provide:

```text
INPUT STATE
CustomerProfileViewModel

ACTIONS
updateProfile()
uploadAvatar()
deleteAccount()

AVAILABLE COMPONENTS
Button
Avatar
Card
FormField
Modal

DESIGN TOKENS
spacing.*
color.*
typography.*

REQUIRED STATES
loading
loaded
validation error
save error
empty avatar

VIEWPORTS
mobile
tablet
desktop
```

The solver is free to create the page composition while remaining unable to invent a new backend capability or bypass the generated application interface.

Verification can combine hard gates and soft evaluation.

Hard gates might include:

```text
compile
component contract
required states
accessibility baseline
interaction tests
allowed imports
```

Soft evaluation might include:

```text
visual hierarchy
spacing quality
consistency
responsive composition
```

Hard correctness and subjective quality must not be collapsed into one score.

---

## Immediate feedback instead of long context

The Box should favor short corrective loops.

Bad pattern:

```text
agent receives whole repository
        ↓
agent makes many changes
        ↓
one large test run
        ↓
large ambiguous failure set
        ↓
agent rereads repository
```

Preferred pattern:

```text
small Box context
      ↓
small candidate change
      ↓
focused verifier
      ↓
structured counterexample
      ↓
small repair
```

For example:

```text
TYPE_GATE       PASS
COMPILE_GATE    PASS
CONTRACT_GATE   FAIL

scenario:
carrier returns 429

expected:
CarrierUnavailable(retryAfter=30)

received:
UnhandledHttpException
```

The feedback itself becomes part of the next minimal context.

This is the sense in which a Box can provide an **immediate reward signal** without depending on vague model self-evaluation.

Prefer concrete pass/fail evidence and counterexamples over a single scalar reward whenever possible.

---

## Hard gates and quality objectives

A Box should distinguish correctness requirements from optimization goals.

### Hard gates

A candidate cannot be accepted if a required hard gate fails.

Examples:

- invalid types;
- compile failure;
- broken contract scenario;
- unauthorized dependency;
- forbidden network destination;
- mutation outside the Box workspace;
- missing required UI state;
- violated invariant.

### Quality objectives

Quality objectives rank or improve otherwise valid candidates.

Examples:

- visual quality;
- readability;
- maintainability;
- performance within an acceptable range;
- simplicity;
- provider-specific idiomatic behavior.

A quality evaluator must not silently redefine the canonical software contract.

---

## Capability boundaries

One of the strongest consequences of Box Engineering is that software architecture can help define agent and implementation permissions.

A pure pricing function may need:

```text
read input
read configuration
return result
```

It should not automatically receive:

```text
network
filesystem
database
shell
secrets
```

An external payment adapter may need:

```text
HTTP access to one provider
one provider secret
logger
clock
```

but still not need unrestricted repository or database access.

This can reduce the blast radius of both buggy code and autonomous solvers.

The exact enforcement mechanism may vary by execution environment. Dryv should describe capabilities portably and let execution infrastructure map those declarations into real sandbox controls where possible.

---

## Traceability

Every Box should remain explainable in the same way generated output is explainable.

A user should be able to ask:

- which authored semantic item ultimately caused this Box to exist;
- which Canonical IR subject it refers to;
- which pack declared the implementation obligation;
- why the pack could not or chose not to render the implementation directly;
- which context was supplied;
- which files the Box owns;
- which capabilities it receives;
- which verifier accepted the implementation;
- which contract version the implementation was verified against.

Conceptually:

```text
Authoring definition
      ↓
Canonical IR subject
      ↓
Pack selection
      ↓
Implementation obligation
      ↓
BoxSpec
      ↓
Candidate implementation
      ↓
Verification evidence
```

Traceability must work in both directions.

---

## Staleness and incremental maintenance

Accepted custom code should not become invisible to future generation.

A Box can record hashes or identities for the contracts it was verified against.

Suppose an implementation was accepted against:

```text
Shipment contract hash: ac72...
```

Later the canonical definition changes and produces:

```text
Shipment contract hash: 3f91...
```

Dryv should be able to identify the implementation as potentially stale:

```text
STALE IMPLEMENTATION BOX

carrier-quote

Reason:
Shipment contract changed.

Previously verified against:
ac72...

Current:
3f91...
```

This enables incremental AI-assisted or human maintenance:

```text
change authored definition
        ↓
new Canonical IR
        ↓
new generation plan
        ↓
identify affected generated artifacts
        +
identify affected accepted Boxes
        ↓
re-render deterministic output
        +
re-verify only affected custom implementations
```

That is much more efficient than asking an agent to rediscover dependency impact from a large repository after every change.

---

## Contract strength is the limiting factor

Box Engineering is only as trustworthy as the contract and verifier surrounding the implementation.

A weak contract can be satisfied by an incorrect implementation.

A weak test suite can accept code that passes examples while violating the real requirement.

Therefore:

```text
strong contract
    +
strong verifier
    +
bounded implementation space
    ↓
high-confidence implementation
```

but:

```text
weak contract
    +
weak verifier
    ↓
implementation optimized for incomplete evidence
```

This suggests a long-term improvement direction for Codepot/Dryv contracts.

Where justified by actual software meaning, the canonical model may eventually need to represent more than type signatures, including concepts such as:

- preconditions;
- postconditions;
- invariants;
- declared errors;
- state transitions;
- authorization requirements;
- effects;
- idempotency;
- examples;
- behavioral properties;
- timing or timeout semantics where meaningful;
- resource ownership.

These concepts must only enter Canonical IR when they are genuine software semantics. They must not be added merely to improve AI prompts.

---

## Determinism model

Dryv must preserve a precise determinism claim.

### Deterministic

The following should remain deterministic for the same normalized inputs:

- Canonical IR validation;
- pack selection;
- obligation selection;
- Box specification construction;
- context identities and hashes;
- workspace declarations;
- capability declarations;
- acceptance gate declarations;
- generation planning;
- template rendering where the selected renderer is deterministic under the existing Dryv contract;
- deterministic verification steps.

### Potentially nondeterministic

The following may be nondeterministic:

- AI-generated candidate implementation;
- model choice;
- model sampling;
- iterative repair strategy;
- subjective evaluator results.

These must not be silently included in Dryv's deterministic generation guarantee.

An accepted candidate can still become reproducible as a normal source artifact once its exact bytes are committed or otherwise pinned.

---

## Portability

A Box should remain portable across solver implementations.

Bad design:

```yaml
model: claude-x
prompt: |
  Please implement...
```

Better design:

```text
semantic subject
required interface
available context
workspace
capabilities
constraints
acceptance
```

A solver adapter can translate the portable Box contract into:

- an LLM prompt;
- MCP tools;
- a local sandbox;
- a CI job;
- an IDE task;
- a human-readable implementation ticket;
- a synthesis engine input.

This keeps the Dryv contract stable even when AI tooling changes rapidly.

---

## Human and AI parity

A central design principle should be:

> Humans and AI agents solve the same Box contract.

The system should not maintain one hidden set of instructions for an AI and another source of truth for developers.

A developer should be able to run something conceptually equivalent to:

```text
dryv box inspect carrier-quote
```

and see exactly:

- the goal;
- required interface;
- inputs and outputs;
- owned files;
- available dependencies;
- restrictions;
- acceptance checks;
- current verification status.

The same information can be supplied through a machine protocol to an AI solver.

---

## Possible Box lifecycle

The exact states are not designed, but a useful conceptual lifecycle is:

```text
planned
   ↓
unsolved
   ↓
candidate
   ↓
verification failed ──→ candidate
   ↓
verified
   ↓
stale after dependency/contract change
   ↓
reverification or repair
```

Do not confuse a Box lifecycle with application domain state. It is generation and implementation metadata.

---

## Failure reporting

Failure output should be structured and localized.

A solver should receive failures such as:

```text
BOX carrier-quote

Gate: contract-scenario
Status: failed

Subject:
shipping.calculateQuote

Scenario:
provider-timeout

Expected:
CarrierUnavailable

Actual:
TimeoutError escaped adapter boundary

Relevant file:
src/integrations/carrier/quote.ts

Suggested context:
CarrierQuoteProvider
CarrierUnavailable
provider-timeout fixture
```

This is far more useful than an unstructured build transcript containing unrelated project failures.

---

## Security considerations

Box Engineering can improve agent safety, but only if capability declarations are actually enforced where possible.

Important principles:

- generated and contract files should be read-only to the solver unless explicitly owned;
- writable paths should be minimal;
- secrets should be capability-scoped instead of injected globally;
- network access should be allowlisted when the task permits it;
- shell access should not be assumed;
- verification should detect writes outside the declared workspace;
- solver output should not be trusted because the solver reports success;
- security-sensitive Boxes may require mandatory human review even after automated gates pass;
- a Box must never expose more application data than its implementation requires.

A Box contract is not itself a sandbox. Execution infrastructure must enforce the declared boundary.

---

## Initial feasibility by problem type

The following estimates are architectural judgments, not benchmark claims.

| Problem type | Expected suitability |
| --- | --- |
| serialization and transformation | very high |
| validation logic | very high |
| bounded domain calculations | very high |
| external API adapters | high |
| database adapters behind generated interfaces | high |
| background jobs with clear contracts | high |
| workflow logic with explicit state transitions | high |
| UI integration and component implementation | medium to high |
| visual design | medium; needs quality evaluation |
| vague product behavior | low until contract is clarified |
| security-critical custom code | possible only with stronger verification and review |

The best initial Boxes are problems with:

- clear input/output boundaries;
- small dependency surfaces;
- strong examples or properties;
- deterministic verification;
- meaningful custom implementation that templates cannot express cleanly.

External API adapters and custom pure business functions are therefore strong first prototypes.

---

## What not to do

### Do not turn Runtime IR into a prompt format

Runtime IR represents canonical software meaning.

### Do not let template packs redefine business semantics

A pack may declare how an existing semantic requirement becomes a rendered artifact or bounded implementation obligation. It must not invent a competing domain model.

### Do not make AI mandatory

A Box must remain solvable by a human or another tool.

### Do not accept model self-evaluation as verification

The solver may explain its work, but acceptance must come from declared independent gates.

### Do not expose the whole repository by default

Minimal sufficient context is a feature, not a limitation.

### Do not call nondeterministic synthesis deterministic generation

The boundary must remain explicit in CLI output, metadata, plans, and documentation.

### Do not use a scalar score when a concrete counterexample is available

Structured failures make repair faster and more explainable.

### Do not let a Box silently mutate generated files

Generated artifacts and custom implementation ownership must remain distinct and traceable.

---

## Potential implementation direction

No implementation is approved by this document. A safe exploration sequence would be:

### Phase 1 — contract prototype

Define a solver-neutral `BoxSpec` outside Canonical IR.

Prototype only:

- semantic subject identity;
- one required interface;
- context resources;
- owned path;
- read-only paths;
- acceptance commands or verifier identifiers;
- trace back to pack selection.

Use a pure function or external API adapter as the first example.

### Phase 2 — deterministic Box planning

Determine whether implementation obligations should be:

- first-class entries in `GenerationPlan`;
- a sibling `ImplementationPlan`;
- or another deterministic plan structure derived from the same normalized inputs.

The choice must preserve the existing Runtime and `dryv-api` boundaries.

### Phase 3 — verifier protocol

Define a transport-neutral verification result containing:

- gate identifier;
- status;
- diagnostics;
- counterexamples;
- relevant semantic subjects;
- relevant files;
- evidence hashes.

### Phase 4 — human workflow

Prove the Box is useful without AI.

A developer should be able to inspect, implement, and verify one Box using normal project tooling.

### Phase 5 — AI solver adapter

Add one replaceable solver integration.

The solver adapter receives the same Box contract and must not become part of Canonical IR or pack semantics.

### Phase 6 — staleness and incremental repair

Track which accepted implementation depends on which Box inputs and invalidate verification evidence when relevant contracts change.

### Phase 7 — richer capability enforcement

Map declared Box capabilities to actual sandbox, network, filesystem, secret, and tool restrictions where the execution environment supports them.

---

## Questions that must be answered before implementation

1. What is the smallest first-class representation of an implementation obligation?
2. Does the obligation belong directly in `GenerationPlan`, beside it, or in a later execution layer?
3. Which part of a pack declares that a requirement is custom implementation rather than a render job?
4. How does a pack identify the interface or semantic surface that the custom implementation must satisfy?
5. How are Box-owned files distinguished from generated artifacts?
6. How are project-specific paths resolved without weakening the existing Project Client filesystem boundary?
7. Which verification gates are portable and which are project/runtime specific?
8. How are external provider fixtures supplied without embedding provider semantics into Canonical IR?
9. How are secret capabilities represented without putting secret values into plans or Box metadata?
10. How does the system prove that generated context is minimal enough while still complete enough?
11. What causes an accepted Box implementation to become stale?
12. How is verification evidence stored without treating it as canonical software meaning?
13. How does a solver request more context without gaining unrestricted repository access?
14. How are subjective UI quality checks separated from hard contract correctness?
15. What parts of verification are deterministic enough to participate in Dryv's reproducibility guarantees?

---

## Architectural invariants

If Box Engineering becomes part of Dryv, these rules should remain non-negotiable:

1. Canonical Dryv Runtime IR remains the only semantic authority.
2. Authoring continues to define software, not solver behavior.
3. Packs define how canonical meaning maps to generated output and implementation obligations.
4. Runtime planning remains deterministic.
5. AI execution is not part of canonical generation semantics.
6. A Box is solver-neutral.
7. A human can inspect and solve the same Box an AI receives.
8. Generated files and custom implementation ownership remain explicit.
9. Verification is independent of solver claims.
10. Contract failures are reported as structured evidence where possible.
11. Capability boundaries are explicit and enforceable where the execution platform supports them.
12. Accepted custom implementations remain traceable to the semantic subjects and contracts they satisfy.
13. Contract changes can invalidate stale verification evidence.
14. Graph orchestration may compose Boxes later but is not required for the Box model itself.
15. Box Engineering must strengthen, not weaken, determinism, portability, explainability, and architectural separation.

---

## Long-term interpretation

The deeper opportunity is to change the role of code generation.

Traditional generation assumes:

```text
description
    ↓
generator
    ↓
source code
```

Box Engineering allows:

```text
description
    ↓
Canonical Runtime IR
    ↓
deterministic planning
    ↓
┌──────────────────────────────┐
│ fully generatable work       │──→ generated artifacts
└──────────────────────────────┘

┌──────────────────────────────┐
│ non-generatable custom work  │──→ bounded Boxes
└──────────────────────────────┘
                                      ↓
                                human / AI solver
                                      ↓
                                  verifier
                                      ↓
                              accepted custom code
```

That means Codepot/Dryv does not have to know how to deterministically render every line of software in order to control the architecture of the resulting system.

It can instead ensure that every custom line has an explicit place, an explicit contract, an explicit dependency surface, and an explicit reason for being accepted.

The resulting model is:

> **Generated where deterministic. Bounded where custom. Verified at the boundary.**

Or more formally:

> Dryv compiles software intent into deterministic generated artifacts and bounded implementation obligations. Each obligation exposes a minimal typed world containing what an implementation may consume, what it must produce, the effects it may perform, the source surface it owns, and the evidence required for acceptance. Humans and AI agents may fulfill those obligations without becoming authorities over the surrounding architecture.

The intelligence may operate inside the box.

The architecture remains outside it.
