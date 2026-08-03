import React from "react";

/**
 * Recursively extracts plain text from any React node tree.
 * This is critical for when rehype plugins or syntax transformers 
 * wrap code tokens in <span> elements — you need the raw string, 
 * not the element tree.
 */
export function extractText(node: React.ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (React.isValidElement(node)) {
    return extractText((node.props as { children?: React.ReactNode }).children);
  }
  return "";
}
