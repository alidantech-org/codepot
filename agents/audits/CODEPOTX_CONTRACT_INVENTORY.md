# CodepotX contract inventory

Date: 2026-07-23
Branch: `chatgpt/codepotx-restart`
Task: 17
Issue: #15

## Supported consumer paths

- `codepotx` re-exports the supported contract types used by authoring consumers.
- `codepotx/contract` is the complete stable contract facade.
- Internal package code primarily imports through `@/contract/index`.
- Existing flat source modules under `src/contract/*.types.ts` remain compatibility shims during the structure migration.

No new package subpath is introduced by Task 17. The nested files below establish internal ownership; the supported package facade remains `codepotx/contract`.

## Protocol

Owner: `src/contract/protocol/`

Symbols:

- `CODEPOT_PROTOCOL_VERSION`
- `CODEPOT_ARTIFACT_VERSION`
- `CodepotProtocolVersion`
- `CodepotArtifactVersion`
- `ArtifactKind`
- `ArtifactProducer`
- `ArtifactHeader`
- `ArtifactReference`
- `CompiledDocumentation`
- `CompiledNamedItem`
- `JsonPrimitive`
- `JsonValue`
- `JsonObject`
- `PortablePath`
- `UriString`
- `ContentDigest`
- `IsoTimestamp`
- `CodepotId`
- `Awaitable`
- `Disposable`
- `CancellationSignal`

Compatibility shims:

- `src/contract/artifact.types.ts`
- `src/contract/common.types.ts`

## Sources

Owner: `src/contract/sources/`

Symbols:

- `SourcePosition`
- `SourceRange`
- `SourceFileReference`
- `SourceLocation`
- `LocalSourceDescriptor`
- `PackageSourceDescriptor`
- `GitSourceDescriptor`
- `ArtifactSourceDescriptor`
- `MemorySourceDescriptor`
- `SourceDescriptor`
- `ResolvedSource`

Compatibility shim: `src/contract/sources.types.ts`.

## Diagnostics and operation results

Owner: `src/contract/diagnostics/`

Symbols:

- `DiagnosticSeverity`
- `DiagnosticLayer`
- `RelatedDiagnostic`
- `Diagnostic`
- `ValidationResult`
- `OperationSuccess`
- `OperationFailure`
- `OperationResult`

Compatibility shim: `src/contract/diagnostics.types.ts`.

## Authoring artifacts

Owner: `src/contract/artifacts/authoring/`

Symbols:

- `CompiledPrimitiveKind`
- `CompiledSchemaConstraint`
- `CompiledSchemaUsageBase`
- `CompiledSchemaReferenceUse`
- `CompiledInlineSchemaUse`
- `CompiledSchemaUse`
- `CompiledPrimitiveSchema`
- `CompiledLiteralSchema`
- `CompiledEnumOption`
- `CompiledEnumSchema`
- `CompiledFieldLifecycle`
- `CompiledFieldQuery`
- `CompiledField`
- `CompiledObjectSchema`
- `CompiledArraySchema`
- `CompiledTupleSchema`
- `CompiledUnionSchema`
- `CompiledRecordSchema`
- `CompiledFileSchema`
- `CompiledNoContentSchema`
- `CompiledInlineSchema`
- `CompiledSchema`
- `CompiledPropertyGroup`
- `CompiledEntityConstraint`
- `CompiledEntity`
- `CompiledRelation`
- `CompiledAccessDefinition`
- `CompiledHook`
- `CompiledFrontend`
- `CompiledHttpMethod`
- `CompiledParameterLocation`
- `CompiledParameter`
- `CompiledMediaTypeSchema`
- `CompiledRequestBody`
- `CompiledResponse`
- `CompiledOperationEffect`
- `CompiledOperation`
- `CompiledResource`
- `CompiledProject`
- `CompiledAuthoringArtifact`

Compatibility shim: `src/contract/authoring-artifact.types.ts`.

## Templating artifacts and introspection data

Owner: `src/contract/artifacts/templating/`

Symbols:

- `TemplateSelectionMode`
- `FileLifecycleMode`
- `FileCompareMode`
- `CompiledPathToken`
- `CompiledTemplateFolder`
- `CompiledWritePolicy`
- `CompiledTemplateDescriptor`
- `TemplatePackManifest`
- `CompiledTemplatePack`
- `TemplateVariableKind`
- `TemplateVariableScope`
- `TemplateVariableOriginLayer`
- `TemplateVariableOrigin`
- `TemplateVariableEntry`
- `TemplateHelperArgument`
- `TemplateHelperDescriptor`
- `TemplatePartialDescriptor`
- `TemplateReferenceKind`
- `TemplateReferenceLocation`
- `TemplateReference`
- `TemplateVariableRequirement`
- `TemplateReferenceValidation`
- `TemplateVariableCatalog`
- `TemplateContextValidation`

Compatibility shims:

- `src/contract/template-artifact.types.ts`
- `src/contract/template-variables.types.ts`

## Generation artifacts and outcomes

Owner: `src/contract/artifacts/generation/`

Symbols:

- `PlannedDependency`
- `PlannedFile`
- `PlannedCommand`
- `PlannedCleanOperation`
- `GenerationPlan`
- `Utf8VirtualFileContent`
- `Base64VirtualFileContent`
- `VirtualFileContent`
- `VirtualFile`
- `RenderedGeneration`
- `FileWriteStatus`
- `FileWriteOutcome`
- `CommandExecutionOutcome`
- `ManagedFileRecord`
- `GenerationManifest`
- `GenerationFileCounts`
- `GenerationReport`
- `GenerationResult`

Compatibility shim: `src/contract/generation-artifact.types.ts`.

## Authoring operations

Owner: `src/contract/operations/authoring/`

Symbols:

- `AuthoringCompileRequest`
- `AuthoringValidateRequest`
- `AuthoringInspectRequest`
- `AuthoringArtifactLoadRequest`
- `AuthoringCacheRequest`
- `AuthoringCompileResult`
- `AuthoringValidateResult`
- `AuthoringInspectResult`
- `AuthoringArtifactLoadResult`
- `AuthoringCacheResult`

Shared operation symbol: `CacheMode` in `src/contract/operations/cache-mode.types.ts`.

## Templating operations

Owner: `src/contract/operations/templating/`

Symbols:

- `TemplatingLoadRequest`
- `TemplatingValidateRequest`
- `TemplatingCompileRequest`
- `TemplateContextRequest`
- `TemplateVariablesRequest`
- `TemplateContextValidateRequest`
- `TemplateRenderRequest`
- `TemplatingLoadResult`
- `TemplatingValidateResult`
- `TemplatingCompileResult`
- `TemplateContextResult`
- `TemplateVariablesResult`
- `TemplateContextValidateResult`
- `TemplateRenderResult`

## Generation operations

Owner: `src/contract/operations/generation/`

Symbols:

- `CodepotFileLoadRequest`
- `CodepotCommandConfig`
- `CodepotTaskConfig`
- `CompiledCodepotFile`
- `GenerationPlanRequest`
- `GenerationRenderRequest`
- `GenerationWriteRequest`
- `GenerationCleanRequest`
- `GenerationCommandRequest`
- `GenerationExecuteRequest`
- `CodepotFileLoadResult`
- `GenerationPlanResult`
- `GenerationRenderResult`
- `GenerationWriteResult`
- `GenerationCleanResult`
- `GenerationCommandResult`
- `GenerationExecuteResult`

The combined operation compatibility shim is `src/contract/requests.types.ts`.

## Runtime operations

Owner: `src/contract/operations/runtime/`

Symbols:

- `RuntimeLayer`
- `RuntimeFeature`
- `RuntimeFeatureQuery`
- `RuntimeFeatureResult`
- `RunContext`
- `RuntimeOperationMap`
- `RuntimeOperationKind`
- `RuntimeRequest`
- `RuntimeResponse`

`CodepotRuntimePort` is owned by the runtime engine-port module. The compatibility shim `src/contract/runtime.types.ts` re-exports both surfaces.

## Events

Owner: `src/contract/events/`

Symbols:

- `EventEnvelope`
- `RuntimeStartedPayload`
- `RuntimeCompletedPayload`
- `RuntimeFailedPayload`
- `StagePayload`
- `SourceResolvedPayload`
- `ArtifactCreatedPayload`
- `GenerationTaskPayload`
- `GenerationPlanPayload`
- `FileLifecyclePayload`
- `CommandLifecyclePayload`
- `DiagnosticPublishedPayload`
- `CodepotEvent`
- `CodepotEventType`
- `CodepotEventOf`
- `CodepotEventListener`

Compatibility shim: `src/contract/events.types.ts`.

## Infrastructure ports

Owner: `src/contract/ports/infrastructure/`

Symbols:

- `FileKind`
- `FileStat`
- `DirectoryEntry`
- `GlobOptions`
- `RemoveOptions`
- `FileSystemPort`
- `CompareFileRequest`
- `CompareFileResult`
- `WriteFileRequest`
- `WriteBatchRequest`
- `FileWriterPort`
- `DataCodecPort`
- `ModuleLoadOptions`
- `LoadedModule`
- `ModuleLoaderPort`
- `SourceResolveOptions`
- `SourceResolverPort`
- `HashPort`
- `CachePayload`
- `CacheEntry`
- `CachePort`
- `CommandRequest`
- `CommandResult`
- `CommandRunnerPort`
- `ClockPort`
- `IdPort`
- `EventBusPort`

## Engine ports

Owner: `src/contract/ports/engines/`

Symbols:

- `AuthoringPort`
- `TemplatingPort`
- `TemplateIntrospectionPort`
- `GenerationPort`
- `CodepotRuntimePort`

Compatibility shims:

- `src/contract/ports.types.ts`
- `src/contract/template-introspection.types.ts`

## Public facade invariant

`src/contract/index.ts` exports constants from `protocol/` and type-only surfaces from:

1. `protocol/`
2. `sources/`
3. `diagnostics/`
4. `artifacts/`
5. `operations/`
6. `events/`
7. `ports/`

Later tasks may remove compatibility shims only after supported consumers and declaration output prove they are unnecessary. Task 17 does not remove them.
