---
title: Dryv authoring
product: dryv-author
description: Express software meaning and compile it into canonical Runtime IR.
---

# Dryv authoring

Authoring is the human- and machine-friendly entry layer.

It may provide helpers, builders, validation, reusable patterns, and organization for large software blueprints. Its output is canonical Runtime IR.

## Authoring owns

- expressing software meaning;
- validating authored definitions;
- creating explicit references and relationships;
- reducing repetition without hiding behavior;
- compiling into Runtime IR.

## Authoring does not own

- target source generation;
- pack selection;
- output destinations;
- file writes;
- Runtime IR serialization;
- a second semantic model.

Natural language may help a human or AI propose authoring changes, but validated formal authoring—not prose—is the semantic input to the runtime.
