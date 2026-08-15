import { createHash } from 'node:crypto';
import readline from 'node:readline';
import Handlebars from 'handlebars';

const RENDERER_ID = 'handlebars';
const RENDERER_VERSION = '4.7.9';
const CAPABILITY = 'handlebars/v1';
const revision = process.env.DRYV_RENDERER_REVISION ?? 'default';
const fingerprint = sha256(`dryv-handlebars\0${RENDERER_VERSION}\0${revision}\0strict-v1`);
const cancelled = new Set();

const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });

for await (const line of input) {
  let response;
  try {
    const message = JSON.parse(line);
    response = handle(message);
  } catch (error) {
    response = {
      type: 'protocol-error',
      code: 'HANDLEBARS_PROTOCOL_ERROR',
      message: error instanceof Error ? error.message : String(error),
    };
  }
  process.stdout.write(`${JSON.stringify(response)}\n`);
  if (response.type === 'shutdown-result') process.exit(0);
}

function handle(message) {
  if (!message || typeof message !== 'object' || Array.isArray(message)) {
    throw new Error('protocol message must be an object');
  }
  if (message.type === 'hello') {
    return {
      type: 'hello-result',
      rendererId: RENDERER_ID,
      rendererVersion: RENDERER_VERSION,
      capabilities: [CAPABILITY],
      protocolVersions: [1],
      contextVersions: [1],
      templateMediaTypes: ['text/x-handlebars-template', 'application/x-handlebars-template'],
      fingerprint,
      maxConcurrency: 1,
      deterministic: true,
    };
  }
  if (message.type === 'cancel') {
    requireString(message.jobId, 'jobId');
    cancelled.add(message.jobId);
    return { type: 'cancel-result', jobId: message.jobId };
  }
  if (message.type === 'shutdown') return { type: 'shutdown-result' };
  if (message.type !== 'render') throw new Error(`unknown protocol message type ${String(message.type)}`);

  const request = message.request;
  if (!request || typeof request !== 'object' || Array.isArray(request)) throw new Error('render request must be an object');
  const jobId = requireString(request.jobId, 'jobId');
  if (cancelled.has(jobId)) {
    return { type: 'render-result', jobId, rendererFingerprint: fingerprint, outputs: [], diagnostics: [], cancelled: true };
  }
  if (!Array.isArray(request.outputs) || request.outputs.length !== 1) {
    return {
      type: 'render-result',
      jobId,
      rendererFingerprint: fingerprint,
      outputs: [],
      diagnostics: [{ code: 'HANDLEBARS_OUTPUT_CARDINALITY', message: 'Handlebars Render Client requires one planned output', severity: 'error' }],
      cancelled: false,
    };
  }

  try {
    const source = Buffer.from(requireString(request.templateContentBase64, 'templateContentBase64'), 'base64').toString('utf8');
    const template = Handlebars.compile(source, { strict: true, noEscape: true });
    const rendered = Buffer.from(template(request.context ?? {}), 'utf8');
    const outputId = requireString(request.outputs[0]?.id, 'output.id');
    return {
      type: 'render-result',
      jobId,
      rendererFingerprint: fingerprint,
      outputs: [{
        id: outputId,
        contentBase64: rendered.toString('base64'),
        contentHash: artifactHash(rendered),
      }],
      diagnostics: [],
      cancelled: false,
    };
  } catch (error) {
    return {
      type: 'render-result',
      jobId,
      rendererFingerprint: fingerprint,
      outputs: [],
      diagnostics: [{
        code: 'HANDLEBARS_RENDER_FAILED',
        message: error instanceof Error ? error.message : String(error),
        severity: 'error',
      }],
      cancelled: false,
    };
  }
}

function requireString(value, label) {
  if (typeof value !== 'string' || value.length === 0) throw new Error(`${label} must be a non-empty string`);
  return value;
}

function sha256(value) {
  return `sha256:${createHash('sha256').update(value).digest('hex')}`;
}

function artifactHash(content) {
  return `sha256:v1:artifact-content:${createHash('sha256').update(content).digest('hex')}`;
}
