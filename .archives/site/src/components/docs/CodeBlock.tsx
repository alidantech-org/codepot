"use client";

import { Check, Copy } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { ReactNode, HTMLAttributes } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  oneDark,
  oneLight,
} from "react-syntax-highlighter/dist/esm/styles/prism";
import { useTheme } from "next-themes";
import { cn } from "@/lib/utils";

function extractText(node: ReactNode): string {
  if (typeof node === "string") return node;
  if (typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (
    node &&
    typeof node === "object" &&
    "props" in node &&
    node.props &&
    typeof node.props === "object" &&
    "children" in node.props
  ) {
    return extractText(node.props.children as ReactNode);
  }
  return "";
}

export function CodeBlock(props: HTMLAttributes<HTMLPreElement>) {
  const [copied, setCopied] = useState(false);

  const code = useMemo(
    () => extractText(props.children).trimEnd(),
    [props.children],
  );

  const language = useMemo(() => {
    const raw = props["data-language" as keyof typeof props];
    if (typeof raw === "string" && raw.trim()) return raw;
    const child = (props.children as any)?.props?.className ?? "";
    const match = /language-(\w+)/.exec(child);
    return match?.[1] ?? "typescript"; // fallback to typescript
  }, [props]);

  async function copyCode() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  const { resolvedTheme } = useTheme(); // resolvedTheme handles 'system' preference automatically
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch by only rendering after mounting
  useEffect(() => {
    setMounted(true);
  }, []);

  // Use a fallback or skeleton until the theme is resolved
  if (!mounted) {
    return <div className="h-40 w-full animate-pulse rounded-xl bg-muted" />;
  }

  const isDark = resolvedTheme === "dark";

  return (
    <figure
      className={cn(
        "group my-6 overflow-hidden rounded-xl border border-border shadow-sm",
        isDark ? "bg-[#282c34]" : "bg-[#fafafa]",
      )}
    >
      {/* Header */}
      <div
        className={cn(
          "flex items-center justify-between border-b px-4 py-2",
          isDark ? "border-white/10 bg-white/5" : "border-black/8 bg-black/3",
        )}
      >
        <span
          className={cn(
            "text-xs font-medium uppercase tracking-wide",
            isDark ? "text-white/40" : "text-black/40",
          )}
        >
          {language}
        </span>
        <button
          type="button"
          onClick={copyCode}
          className={cn(
            "inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium transition-colors",
            isDark
              ? "text-white/40 hover:bg-white/10 hover:text-white/80"
              : "text-black/40 hover:bg-black/5 hover:text-black/70",
          )}
          aria-label={copied ? "Copied code" : "Copy code"}
        >
          {copied ? (
            <>
              <Check className="size-3.5" /> Copied
            </>
          ) : (
            <>
              <Copy className="size-3.5" /> Copy
            </>
          )}
        </button>
      </div>

      <SyntaxHighlighter
        language={language}
        style={isDark ? oneDark : oneLight}
        PreTag="div"
        customStyle={{
          margin: 0,
          padding: "1rem",
          fontSize: "0.875rem",
          lineHeight: "1.5",
          background: "transparent",
        }}
        codeTagProps={{
          style: {
            display: "block",
            fontFamily:
              "var(--font-mono, ui-monospace, 'Cascadia Code', monospace)",
          },
        }}
      >
        {code}
      </SyntaxHighlighter>
    </figure>
  );
}
