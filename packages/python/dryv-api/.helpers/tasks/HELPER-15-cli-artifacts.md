# HELPER-15 — CLI artifact stream and bundle handling

Status: TODO
Prerequisite: HELPER-14 DONE.

## Goal
Accept both live WebSocket artifact streaming and deterministic ZIP bundle delivery without creating two filesystem/application paths.

## Required structure
Implement `artifacts/model.py`, `stream.py`, `bundle.py`, `manifest.py`, and `verify.py`.

Both transports must normalize into one verified artifact representation/ArtifactSet containing logical artifact identity, intended relative path, content/hash and available provenance/metadata.

Required verification includes artifact IDs, normalized safe relative paths, stream chunk offsets/order, declared sizes, SHA-256/content hashes and bundle manifest consistency. Large files/builds must be handled without unbounded whole-build memory growth.

## Enforcement
A transport may not apply files directly. Do not trust server/client-declared hashes without verifying received bytes. Reject duplicate artifact IDs/paths and incomplete streams. Preserve backpressure rather than accumulating arbitrary queued content.

## Completion
Downstream filesystem code receives the same verified model regardless of `stream` or `bundle` delivery. No tests yet.