"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = require("vscode");
const LANGUAGE_ID_PREFIX = "codepurify";
const BLOCK_NAMES = ["if", "loop", "ignore", "unless", "with"];
const ELSE_PARENT_BLOCKS = ["if", "unless"];
function activate(context) {
    console.log("Codepurify extension activated");
    vscode.window.setStatusBarMessage("✨ Codepurify ready — template syntax active", 4000);
    context.subscriptions.push(registerCompletionProvider(), registerDiagnosticsProvider(context));
}
exports.activate = activate;
function deactivate() { }
exports.deactivate = deactivate;
function isCodepurifyDocument(document) {
    return (document.languageId === LANGUAGE_ID_PREFIX ||
        document.languageId.startsWith(`${LANGUAGE_ID_PREFIX}-`) ||
        document.fileName.endsWith(".codepurify") ||
        document.fileName.endsWith(".code"));
}
function registerCompletionProvider() {
    return vscode.languages.registerCompletionItemProvider({ scheme: "file", pattern: "**/*.{codepurify,code}" }, {
        provideCompletionItems(document) {
            if (!isCodepurifyDocument(document))
                return undefined;
            return [
                snippet("if", "{|if ${1:condition}|}\n\t$0\n{|/if|}", "If block"),
                snippet("ifelse", "{|if ${1:condition}|}\n\t${2:then}\n{|else|}\n\t${3:else}\n{|/if|}", "If / else block"),
                snippet("loop", "{|loop ${1:item} in ${2:collection}|}\n\t$0\n{|/loop|}", "Loop block"),
                snippet("unless", "{|unless ${1:condition}|}\n\t$0\n{|/unless|}", "Unless block"),
                snippet("unlesselse", "{|unless ${1:condition}|}\n\t${2:then}\n{|else|}\n\t${3:else}\n{|/unless|}", "Unless / else block"),
                snippet("with", "{|with ${1:value}|}\n\t$0\n{|/with|}", "With block"),
                snippet("ignore", "{|ignore|}\n\t$0\n{|/ignore|}", "Ignore block"),
                snippet("else", "{|else|}", "Else branch"),
                snippet("comment", "{|# ${1:comment} #|}", "Comment"),
                snippet("doc", "{|* ${1:documentation} *|}", "Documentation comment"),
            ];
        },
    }, "!", "{");
}
function snippet(label, body, detail) {
    const item = new vscode.CompletionItem(label, vscode.CompletionItemKind.Snippet);
    item.insertText = new vscode.SnippetString(body);
    item.detail = detail;
    return item;
}
function registerDiagnosticsProvider(context) {
    const collection = vscode.languages.createDiagnosticCollection("codepurify");
    const validate = (document) => {
        if (!isCodepurifyDocument(document))
            return;
        const diagnostics = [];
        const text = document.getText();
        validateDelimiters(document, text, diagnostics);
        validateBlocks(document, text, diagnostics);
        collection.set(document.uri, diagnostics);
    };
    vscode.workspace.textDocuments.forEach(validate);
    context.subscriptions.push(vscode.workspace.onDidOpenTextDocument(validate), vscode.workspace.onDidChangeTextDocument((event) => validate(event.document)), vscode.workspace.onDidCloseTextDocument((document) => collection.delete(document.uri)), collection);
    return collection;
}
function validateDelimiters(document, text, diagnostics) {
    const openCount = countMatches(text, /\{\|/g);
    const closeCount = countMatches(text, /\|\}/g);
    if (openCount !== closeCount) {
        diagnostics.push(createDiagnostic(document, 0, 0, `Mismatched delimiters: found ${openCount} "{|" and ${closeCount} "|}".`, vscode.DiagnosticSeverity.Error));
    }
}
function validateBlocks(document, text, diagnostics) {
    const tagRegex = /\{\|\s*(\/)?\s*([a-zA-Z_][a-zA-Z0-9_]*)\b[\s\S]*?\|\}/g;
    const stack = [];
    let match;
    while ((match = tagRegex.exec(text)) !== null) {
        const isClosing = Boolean(match[1]);
        const name = match[2];
        if (name === "else") {
            validateElse(document, match, stack, diagnostics);
            continue;
        }
        if (!BLOCK_NAMES.includes(name))
            continue;
        if (!isClosing) {
            stack.push({ name, index: match.index, hasElse: false });
            continue;
        }
        const last = stack.pop();
        if (!last) {
            diagnostics.push(createDiagnostic(document, match.index, match[0].length, `Unexpected closing block "{|/${name}|}".`, vscode.DiagnosticSeverity.Error));
            continue;
        }
        if (last.name !== name) {
            diagnostics.push(createDiagnostic(document, match.index, match[0].length, `Mismatched closing block. Expected "{|/${last.name}|}" but found "{|/${name}|}".`, vscode.DiagnosticSeverity.Error));
        }
    }
    for (const unclosed of stack) {
        diagnostics.push(createDiagnostic(document, unclosed.index, 0, `Unclosed block "{|${unclosed.name}|}".`, vscode.DiagnosticSeverity.Error));
    }
}
function validateElse(document, match, stack, diagnostics) {
    const parent = stack[stack.length - 1];
    if (!parent) {
        diagnostics.push(createDiagnostic(document, match.index, match[0].length, `"else" must be inside an "if" or "unless" block.`, vscode.DiagnosticSeverity.Error));
        return;
    }
    if (!ELSE_PARENT_BLOCKS.includes(parent.name)) {
        diagnostics.push(createDiagnostic(document, match.index, match[0].length, `"else" is not allowed inside "${parent.name}".`, vscode.DiagnosticSeverity.Error));
        return;
    }
    if (parent.hasElse) {
        diagnostics.push(createDiagnostic(document, match.index, match[0].length, `Duplicate "else" inside "${parent.name}" block.`, vscode.DiagnosticSeverity.Error));
        return;
    }
    parent.hasElse = true;
}
function createDiagnostic(document, index, length, message, severity) {
    const start = document.positionAt(index);
    const end = document.positionAt(index + length);
    return new vscode.Diagnostic(new vscode.Range(start, end), message, severity);
}
function countMatches(text, regex) {
    return [...text.matchAll(regex)].length;
}
//# sourceMappingURL=extension.js.map