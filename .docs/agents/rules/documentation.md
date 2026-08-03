# Documentation rules

## Single source

`.docs/` is the only canonical authored documentation system.

Applications and packages may keep one concise root `README.md` containing status, purpose, essential local commands, boundaries, and links to `.docs`. Do not add package- or app-local architecture folders, tasks, plans, audits, deployment guides, agent rules, or contribution documents.

## Ownership

- Project identity and status: `.docs/project/`
- Approved architecture: `.docs/architecture/`
- Product documentation: `.docs/products/`
- Application documentation: `.docs/apps/`
- Agent procedures: `.docs/agents/`
- Tasks and work evidence: `.docs/tasks/`
- Decisions: `.docs/decisions/`
- Audits: `.docs/audits/`
- Operations: `.docs/operations/`
- Public website content: `.docs/public/`
- Research: `.docs/research/`
- Existing planning papers: `.docs/plan/`

## Editing

- Update the canonical document instead of creating a competing explanation.
- Prefer links over duplicated rules.
- Distinguish current implementation, approved design, planned work, frozen behavior, and historical evidence.
- Do not claim tests or implemented behavior in documentation without evidence.
- Preserve public URLs through navigation redirects when moving published content.
- Generated documentation files and template files are implementation artifacts and must not be edited as canonical prose.
