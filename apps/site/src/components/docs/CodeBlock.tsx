"use client";

import type { HTMLAttributes, ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { Check, Copy } from "lucide-react";
import { useTheme } from "next-themes";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark, oneLight } from "react-syntax-highlighter/dist/esm/styles/prism";

import { cn } from "@/lib/utils";

function extractText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (node && typeof node === "object" && "props" in node) {
    const props = node.props as { children?: ReactNode };
    return extractText(props.children);
  }
  return "";
}

export function CodeBlock(props: HTMLAttributes<HTMLPreElement>) {
  const [copied, setCopied] = useState(false);
  const [mounted, setMounted] = useState(false);
  const { resolvedTheme } = useTheme();
  const code = useMemo(() => extractText(props.children).trimEnd(), [props.children]);
  const language = useMemo(() => {
    const child = props.children as { props?: { className?: string } } | undefined;
    const match = /language-(\w+)/.exec(child?.props?.className ?? "");
    return match?.[1] ?? "typescript";
  }, [props.children]);

  useEffect(() => setMounted(true), []);

  async function copyCode() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  if (!mounted) return <div className="h-40 w-full animate-pulse rounded-xl bg-muted" />;
  const isDark = resolvedTheme === "dark";

  return (
    <figure className={cn("group my-6 overflow-hidden rounded-xl border border-border shadow-sm", isDark ? "bg-[#282c34]" : "bg-[#fafafa]")}>
      <div className={cn("flex items-center justify-between border-b px-4 py-2", isDark ? "border-white/10 bg-white/5" : "border-black/8 bg-black/3")}>
        <span className={cn("text-xs font-medium uppercase tracking-wide", isDark ? "text-white/40" : "text-black/40")}>{language}</span>
        <button type="button" onClick={copyCode} aria-label={copied ? "Copied code" : "Copy code"} className={cn("inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium transition-colors", isDark ? "text-white/40 hover:bg-white/10 hover:text-white/80" : "text-black/40 hover:bg-black/5 hover:text-black/70")}>
          {copied ? <><Check className="size-3.5" />Copied</> : <><Copy className="size-3.5" />Copy</>}
        </button>
      </div>
      <SyntaxHighlighter
        language={language}
        style={isDark ? oneDark : oneLight}
        PreTag="div"
        customStyle={{ margin: 0, padding: "1rem", fontSize: "0.875rem", lineHeight: "1.5", background: "transparent" }}
        codeTagProps={{ style: { display: "block", fontFamily: "var(--font-mono, ui-monospace, 'Cascadia Code', monospace)" } }}
      >
        {code}
      </SyntaxHighlighter>
    </figure>
  );
}
