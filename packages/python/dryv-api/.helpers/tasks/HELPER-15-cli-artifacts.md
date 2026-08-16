# HELPER-15 — CLI artifact stream and bundle handling

Status: DONE — PRODUCTION REVIEWED
Prerequisite: HELPER-14 DONE.

## Implemented model
Both live WebSocket artifact delivery and deterministic ZIP delivery normalize into one verified, disk-backed `ArtifactSet`. Content is written incrementally to a temporary workspace rather than accumulated as a whole build in memory.

Verification covers planned artifact identity/path, safe relative paths, duplicate ids/paths, stream offsets, base64 transfer, declared sizes, SHA-256 hashes, stream completion, bundle HTTP hash/size metadata, ZIP entry identity, `dryv.bundle/v1` manifest identity and exact GenerationPlan membership.

## Review hardening
Stream delivery now verifies job id, plan index and dependency provenance against the GenerationPlan. Plan parsing rejects duplicate job ids/orders. Bundle manifests additionally verify plan index, semantic ids, subject, pack and template provenance instead of trusting only path/hash membership.

## Enforcement
Artifact transport never writes into the project. The returned temporary artifact set is the only handoff to the filesystem module. Stream mode preserves API backpressure because it consumes the bounded server artifact stream as received.

## Completion
Stream and bundle delivery produce the same verified artifact representation for downstream diff/apply. Production source was reviewed; executable test certification remains separate.
