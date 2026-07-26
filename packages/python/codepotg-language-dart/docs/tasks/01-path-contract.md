# Dart target path-contract tasks

## DART-PATH-001 — Target descriptor and validation

- [ ] Register `.dart` target behavior and final filename validation.
- [ ] Validate Dart library/part filename restrictions without selecting destination directories.
- [ ] Preserve `.dart` while core removes the engine suffix.
- [ ] Expose only typed target metadata through the public path-value registry.

## DART-PATH-002 — Boundary tests

- [ ] Prove the adapter receives an already resolved destination.
- [ ] Prove it never parses named path recipes or dynamic source-path tokens.
- [ ] Prove `package:` and relative import calculation consumes planned artifact locations.
- [ ] Prove it does not add or depend on semantic `fileName`, `filePath`, or `directory` fields.

**Acceptance:** Dart path validation is independently installable and does not own pack folder structure.
