import fs from "node:fs/promises";
import path from "node:path";

const ROOT = process.cwd();

const HOST_LANGUAGES = [
  {
    id: "javascript",
    label: "JavaScript",
    extensions: ["js"],
    scope: "source.js",
  },
  {
    id: "jsx",
    label: "JavaScript React",
    extensions: ["jsx"],
    scope: "source.jsx",
  },
  {
    id: "typescript",
    label: "TypeScript",
    extensions: ["ts"],
    scope: "source.ts",
  },
  {
    id: "tsx",
    label: "TypeScript React",
    extensions: ["tsx"],
    scope: "source.tsx",
  },
  { id: "sql", label: "SQL", extensions: ["sql"], scope: "source.sql" },
  { id: "java", label: "Java", extensions: ["java"], scope: "source.java" },
  { id: "go", label: "Go", extensions: ["go"], scope: "source.go" },
  { id: "rust", label: "Rust", extensions: ["rs"], scope: "source.rust" },
  { id: "python", label: "Python", extensions: ["py"], scope: "source.python" },
  { id: "csharp", label: "C#", extensions: ["cs"], scope: "source.cs" },
  {
    id: "cpp",
    label: "C++",
    extensions: ["cpp", "cc", "cxx", "hpp", "h"],
    scope: "source.cpp",
  },
  { id: "c", label: "C", extensions: ["c"], scope: "source.c" },
  { id: "php", label: "PHP", extensions: ["php"], scope: "source.php" },
  { id: "ruby", label: "Ruby", extensions: ["rb"], scope: "source.ruby" },
  { id: "kotlin", label: "Kotlin", extensions: ["kt"], scope: "source.kotlin" },
  { id: "swift", label: "Swift", extensions: ["swift"], scope: "source.swift" },
  { id: "html", label: "HTML", extensions: ["html"], scope: "text.html.basic" },
  { id: "css", label: "CSS", extensions: ["css"], scope: "source.css" },
  { id: "scss", label: "SCSS", extensions: ["scss"], scope: "source.css.scss" },
  { id: "json", label: "JSON", extensions: ["json"], scope: "source.json" },
  {
    id: "yaml",
    label: "YAML",
    extensions: ["yaml", "yml"],
    scope: "source.yaml",
  },
  {
    id: "markdown",
    label: "Markdown",
    extensions: ["md"],
    scope: "text.html.markdown",
  },
  {
    id: "dockerfile",
    label: "Dockerfile",
    extensions: ["dockerfile"],
    scope: "source.dockerfile",
  },
  {
    id: "shell",
    label: "Shell",
    extensions: ["sh", "bash", "zsh"],
    scope: "source.shell",
  },
  {
    id: "dart",
    label: "Dart",
    extensions: ["dart"],
    scope: "source.dart",
  },
  {
    id: "vue",
    label: "Vue",
    extensions: ["vue"],
    scope: "source.vue",
  },
  {
    id: "svelte",
    label: "Svelte",
    extensions: ["svelte"],
    scope: "source.svelte",
  },
  {
    id: "xml",
    label: "XML",
    extensions: ["xml"],
    scope: "text.xml",
  },
  {
    id: "toml",
    label: "TOML",
    extensions: ["toml"],
    scope: "source.toml",
  },
  {
    id: "graphql",
    label: "GraphQL",
    extensions: ["graphql", "gql"],
    scope: "source.graphql",
  },
];

const basePackagePath = path.join(ROOT, "package.base.json");
const packagePath = path.join(ROOT, "package.json");
const syntaxesDir = path.join(ROOT, "syntaxes", "wrappers");
const supportedPath = path.join(ROOT, "SUPPORTED_LANGUAGES.txt");

const basePackage = JSON.parse(await fs.readFile(basePackagePath, "utf8"));

await fs.mkdir(syntaxesDir, { recursive: true });

const baseLanguages = [
  {
    id: "codepurify",
    aliases: ["Codepurify", "codepurify"],
    extensions: [".codepurify", ".code"],
    configuration: "./config/language-configuration.json",
  },
];

const baseGrammars = [
  {
    language: "codepurify",
    scopeName: "source.codepurify",
    path: "./syntaxes/codepurify.tmLanguage.json",
  },
];

const generatedLanguages = [];
const generatedGrammars = [];

for (const lang of HOST_LANGUAGES) {
  const languageId = `codepurify-${lang.id}`;
  const scopeName = `${lang.scope}.codepurify`;
  const grammarPath = `./syntaxes/wrappers/codepurify-${lang.id}.tmLanguage.json`;

  generatedLanguages.push({
    id: languageId,
    aliases: [`Codepurify ${lang.label}`],
    extensions: lang.extensions.flatMap((ext) => [
      `.${ext}.codepurify`,
      `.${ext}.code`,
    ]),
    configuration: "./config/language-configuration.json",
  });

  generatedGrammars.push({
    language: languageId,
    scopeName,
    path: grammarPath,
  });

  const grammar = {
    name: `Codepurify ${lang.label}`,
    scopeName,
    patterns: [
      { include: "#codepurify-comments" },
      { include: "#codepurify-tags" },
      { include: lang.scope },
    ],
    repository: {
      "codepurify-comments": {
        patterns: [
          {
            name: "comment.block.documentation.codepurify",
            begin: "\\{\\|\\*",
            end: "\\*\\|\\}",
            beginCaptures: {
              0: {
                name: "punctuation.definition.comment.begin.codepurify",
              },
            },
            endCaptures: {
              0: {
                name: "punctuation.definition.comment.end.codepurify",
              },
            },
          },
          {
            name: "comment.block.codepurify",
            begin: "\\{\\|#",
            end: "#\\|\\}",
            beginCaptures: {
              0: {
                name: "punctuation.definition.comment.begin.codepurify",
              },
            },
            endCaptures: {
              0: {
                name: "punctuation.definition.comment.end.codepurify",
              },
            },
          },
        ],
      },
      "codepurify-tags": {
        patterns: [
          {
            name: "meta.embedded.codepurify",
            begin: "\\{\\|",
            beginCaptures: {
              0: {
                name: "punctuation.definition.template.codepurify",
              },
            },
            end: "\\|\\}",
            endCaptures: {
              0: {
                name: "punctuation.definition.template.codepurify",
              },
            },
            patterns: [
              {
                name: "keyword.control.end.codepurify",
                match: "\\/(if|unless|loop|with|ignore)\\b",
              },
              {
                name: "keyword.control.conditional.codepurify",
                match: "\\b(if|unless|else)\\b",
              },
              {
                name: "keyword.control.repeat.codepurify",
                match: "\\b(loop)\\b",
              },
              {
                name: "keyword.control.context.codepurify",
                match: "\\b(with|ignore)\\b",
              },
              {
                name: "keyword.operator.word.codepurify",
                match: "\\b(in|as|and|or|not|is)\\b",
              },
              {
                name: "keyword.operator.comparison.codepurify",
                match: "==|!=|<=|>=|<|>|!",
              },
              {
                name: "constant.language.boolean.codepurify",
                match: "\\b(true|false|null|undefined)\\b",
              },
              {
                name: "constant.numeric.codepurify",
                match: "\\b\\d+(\\.\\d+)?\\b",
              },
              {
                name: "string.quoted.single.codepurify",
                begin: "'",
                end: "'",
              },
              {
                name: "string.quoted.double.codepurify",
                begin: '"',
                end: '"',
              },
              {
                name: "variable.other.codepurify",
                match: "\\b[a-zA-Z_$][a-zA-Z0-9_$.]*\\b",
              },
            ],
          },
        ],
      },
    },
  };

  await fs.writeFile(
    path.join(syntaxesDir, `codepurify-${lang.id}.tmLanguage.json`),
    `${JSON.stringify(grammar, null, 2)}\n`,
  );
}

basePackage.contributes ??= {};
basePackage.contributes.languages = [...baseLanguages, ...generatedLanguages];
basePackage.contributes.grammars = [...baseGrammars, ...generatedGrammars];

await fs.writeFile(packagePath, `${JSON.stringify(basePackage, null, 2)}\n`);

const supported = [
  "Codepurify Supported Languages",
  "",
  "Base extensions:",
  "- .codepurify",
  "- .code",
  "",
  "Host language template extensions:",
  ...HOST_LANGUAGES.flatMap((lang) => [
    "",
    `${lang.label}:`,
    ...lang.extensions.flatMap((ext) => [
      `- .${ext}.codepurify`,
      `- .${ext}.code`,
    ]),
  ]),
].join("\n");

await fs.writeFile(supportedPath, `${supported}\n`);

console.log(
  "Generated package.json, wrapper grammars, and SUPPORTED_LANGUAGES.txt",
);
