# HELPER-02 — Author core registry, references, naming and metadata

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-01 DONE.

## Goal
Build the language-facing foundations used by every Author feature without creating a second semantic model.

## Scope
Implement `core/declarations.py`, `registry.py`, `references.py`, `naming.py`, `metadata.py`, `source.py`, and the required compiler naming infrastructure.

Required capabilities:
- deterministic declaration registration and duplicate detection;
- explicit group/owner provenance and source locations;
- generic AuthorRef foundation plus typed feature refs such as SchemaRef, OperationRef, EventRef, WorkflowRef, StorageRef, PolicyRef, ValueSourceRef and PropertyRef;
- deterministic semantic ID/name allocation and ownership registry;
- symbols resolvable without global mutable state;
- useful diagnostics that identify declaration, owner and source.

## Enforcement
Author refs are authoring conveniences; Canonical IR IDs remain authoritative after compilation. No reference may silently resolve by ambiguous guessing. No process/network/file-generation behavior belongs here. No generic magic registry/plugin discovery.

## Completion
Core represents and registers cross-feature authoring relationships deterministically while feature-specific declarations remain outside core. Production review confirmed the ownership/reference boundary. No tests were added or run.
