"use client";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

interface CodeHighlightProps {
  code: string;
  language?: string;
  className?: string;
}

export function CodeHighlight({ 
  code, 
  language = "typescript", 
  className = "" 
}: CodeHighlightProps) {
  return (
    <SyntaxHighlighter
      language={language}
      style={oneDark}
      customStyle={{
        margin: 0,
        padding: "1rem",
        borderRadius: "0",
        fontSize: "0.875rem",
        background: "var(--background)",
        height: "100%"
      }}
      codeTagProps={{
        style: {
          color: "var(--foreground)",
          fontFamily: "var(--font-mono)",
        },
      }}
      className={className}
    >
      {code}
    </SyntaxHighlighter>
  );
}
