import * as vscode from "vscode";

const LANGUAGE_ID_PREFIX = "codepurify";
const BLOCK_NAMES = ["if", "loop", "ignore", "unless", "with"];
const ELSE_PARENT_BLOCKS = ["if", "unless"];

type OpenBlock = {
  name: string;
  index: number;
  hasElse: boolean;
};

export function activate(context: vscode.ExtensionContext): void {
  console.log("Codepurify extension activated");

  vscode.window.setStatusBarMessage(
    "✨ Codepurify ready — template syntax active",
    4000,
  );

  context.subscriptions.push(
    registerCompletionProvider(),
    registerDiagnosticsProvider(context),
  );
}

export function deactivate(): void {}

function isCodepurifyDocument(document: vscode.TextDocument): boolean {
  return (
    document.languageId === LANGUAGE_ID_PREFIX ||
    document.languageId.startsWith(`${LANGUAGE_ID_PREFIX}-`) ||
    document.fileName.endsWith(".codepurify") ||
    document.fileName.endsWith(".code")
  );
}

function registerCompletionProvider(): vscode.Disposable {
  return vscode.languages.registerCompletionItemProvider(
    { scheme: "file", pattern: "**/*.{codepurify,code}" },
    {
      provideCompletionItems(document) {
        if (!isCodepurifyDocument(document)) return undefined;

        return [
          snippet("if", "{|if ${1:condition}|}\n\t$0\n{|/if|}", "If block"),
          snippet(
            "ifelse",
            "{|if ${1:condition}|}\n\t${2:then}\n{|else|}\n\t${3:else}\n{|/if|}",
            "If / else block",
          ),
          snippet(
            "loop",
            "{|loop ${1:item} in ${2:collection}|}\n\t$0\n{|/loop|}",
            "Loop block",
          ),
          snippet(
            "unless",
            "{|unless ${1:condition}|}\n\t$0\n{|/unless|}",
            "Unless block",
          ),
          snippet(
            "unlesselse",
            "{|unless ${1:condition}|}\n\t${2:then}\n{|else|}\n\t${3:else}\n{|/unless|}",
            "Unless / else block",
          ),
          snippet("with", "{|with ${1:value}|}\n\t$0\n{|/with|}", "With block"),
          snippet("ignore", "{|ignore|}\n\t$0\n{|/ignore|}", "Ignore block"),
          snippet("else", "{|else|}", "Else branch"),
          snippet("comment", "{|# ${1:comment} #|}", "Comment"),
          snippet("doc", "{|* ${1:documentation} *|}", "Documentation comment"),
        ];
      },
    },
    "!",
    "{",
  );
}

function snippet(
  label: string,
  body: string,
  detail: string,
): vscode.CompletionItem {
  const item = new vscode.CompletionItem(
    label,
    vscode.CompletionItemKind.Snippet,
  );
  item.insertText = new vscode.SnippetString(body);
  item.detail = detail;
  return item;
}

function registerDiagnosticsProvider(
  context: vscode.ExtensionContext,
): vscode.Disposable {
  const collection = vscode.languages.createDiagnosticCollection("codepurify");

  const validate = (document: vscode.TextDocument): void => {
    if (!isCodepurifyDocument(document)) return;

    const diagnostics: vscode.Diagnostic[] = [];
    const text = document.getText();

    validateDelimiters(document, text, diagnostics);
    validateBlocks(document, text, diagnostics);

    collection.set(document.uri, diagnostics);
  };

  vscode.workspace.textDocuments.forEach(validate);

  context.subscriptions.push(
    vscode.workspace.onDidOpenTextDocument(validate),
    vscode.workspace.onDidChangeTextDocument((event) =>
      validate(event.document),
    ),
    vscode.workspace.onDidCloseTextDocument((document) =>
      collection.delete(document.uri),
    ),
    collection,
  );

  return collection;
}

function validateDelimiters(
  document: vscode.TextDocument,
  text: string,
  diagnostics: vscode.Diagnostic[],
): void {
  const openCount = countMatches(text, /\{\|/g);
  const closeCount = countMatches(text, /\|\}/g);

  if (openCount !== closeCount) {
    diagnostics.push(
      createDiagnostic(
        document,
        0,
        0,
        `Mismatched delimiters: found ${openCount} "{|" and ${closeCount} "|}".`,
        vscode.DiagnosticSeverity.Error,
      ),
    );
  }
}

function validateBlocks(
  document: vscode.TextDocument,
  text: string,
  diagnostics: vscode.Diagnostic[],
): void {
  const tagRegex = /\{\|\s*(\/)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\b[\s\S]*?\|\}/g;
  const stack: OpenBlock[] = [];

  let match: RegExpExecArray | null;

  while ((match = tagRegex.exec(text)) !== null) {
    const isClosing = Boolean(match[1]);
    const name = match[2];

    if (name === "else") {
      validateElse(document, match, stack, diagnostics);
      continue;
    }

    if (!BLOCK_NAMES.includes(name)) continue;

    if (!isClosing) {
      stack.push({ name, index: match.index, hasElse: false });
      continue;
    }

    const last = stack.pop();

    if (!last) {
      diagnostics.push(
        createDiagnostic(
          document,
          match.index,
          match[0].length,
          `Unexpected closing block "{|/${name}|}".`,
          vscode.DiagnosticSeverity.Error,
        ),
      );
      continue;
    }

    if (last.name !== name) {
      diagnostics.push(
        createDiagnostic(
          document,
          match.index,
          match[0].length,
          `Mismatched closing block. Expected "{|/${last.name}|}" but found "{|/${name}|}".`,
          vscode.DiagnosticSeverity.Error,
        ),
      );
    }
  }

  for (const unclosed of stack) {
    diagnostics.push(
      createDiagnostic(
        document,
        unclosed.index,
        0,
        `Unclosed block "{|${unclosed.name}|}".`,
        vscode.DiagnosticSeverity.Error,
      ),
    );
  }
}

function validateElse(
  document: vscode.TextDocument,
  match: RegExpExecArray,
  stack: OpenBlock[],
  diagnostics: vscode.Diagnostic[],
): void {
  const parent = stack[stack.length - 1];

  if (!parent) {
    diagnostics.push(
      createDiagnostic(
        document,
        match.index,
        match[0].length,
        `"else" must be inside an "if" or "unless" block.`,
        vscode.DiagnosticSeverity.Error,
      ),
    );
    return;
  }

  if (!ELSE_PARENT_BLOCKS.includes(parent.name)) {
    diagnostics.push(
      createDiagnostic(
        document,
        match.index,
        match[0].length,
        `"else" is not allowed inside "${parent.name}".`,
        vscode.DiagnosticSeverity.Error,
      ),
    );
    return;
  }

  if (parent.hasElse) {
    diagnostics.push(
      createDiagnostic(
        document,
        match.index,
        match[0].length,
        `Duplicate "else" inside "${parent.name}" block.`,
        vscode.DiagnosticSeverity.Error,
      ),
    );
    return;
  }

  parent.hasElse = true;
}

function createDiagnostic(
  document: vscode.TextDocument,
  index: number,
  length: number,
  message: string,
  severity: vscode.DiagnosticSeverity,
): vscode.Diagnostic {
  const start = document.positionAt(index);
  const end = document.positionAt(index + length);

  return new vscode.Diagnostic(new vscode.Range(start, end), message, severity);
}

function countMatches(text: string, regex: RegExp): number {
  return [...text.matchAll(regex)].length;
}
