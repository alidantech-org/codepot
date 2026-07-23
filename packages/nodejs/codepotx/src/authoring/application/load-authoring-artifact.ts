import type {
  AuthoringArtifactLoadRequest,
  AuthoringArtifactLoadResult,
  CompiledAuthoringArtifact,
} from '@/contract/index';
import {
  caughtDiagnostic,
  failure,
  success,
} from '@/internal/results/operation-results';
import type { AuthoringEngineDependencies } from '../engine/authoring-engine.types';

export async function loadAuthoringArtifact(
  dependencies: AuthoringEngineDependencies,
  request: AuthoringArtifactLoadRequest,
): Promise<AuthoringArtifactLoadResult> {
  try {
    const resolved = await dependencies.sources.resolve(request.source);
    const text = await dependencies.files.readText(resolved.entry);
    const artifact = dependencies.data.parseJson<CompiledAuthoringArtifact>(text);
    if (artifact.header.kind !== 'codepot.authoring') {
      return failure([{
        code: 'AUTHORING_ARTIFACT_KIND',
        severity: 'error',
        layer: 'authoring',
        message: `Expected codepot.authoring artifact, received ${artifact.header.kind}.`,
      }]);
    }
    if (request.verifyDigest) {
      if (!artifact.header.contentDigest) {
        return failure([{
          code: 'AUTHORING_ARTIFACT_DIGEST',
          severity: 'error',
          layer: 'authoring',
          message: 'Authoring artifact has no content digest.',
        }]);
      }
      const { header: _header, ...body } = artifact;
      const digest = await dependencies.hashes.text(JSON.stringify(body));
      if (digest !== artifact.header.contentDigest) {
        return failure([{
          code: 'AUTHORING_ARTIFACT_DIGEST_MISMATCH',
          severity: 'error',
          layer: 'authoring',
          message: 'Authoring artifact content digest does not match its body.',
        }]);
      }
    }
    return success(artifact);
  } catch (caught) {
    return failure([
      caughtDiagnostic('authoring', 'AUTHORING_ARTIFACT_LOAD_FAILED', caught),
    ]);
  }
}
