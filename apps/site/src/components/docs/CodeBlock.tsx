"use client";

import { Check, Copy } from "lucide-react";
import { useTheme } from "next-themes";
import type { HTMLAttributes, ReactNode } from "react";
import { useMemo, useState, useSyncExternalStore } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import {
  vs,
  vscDarkPlus,
} from "react-syntax-highlighter/dist/esm/styles/prism";

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

function subscribeToHydration(): () => void {
  return () => undefined;
}

export function CodeBlock(props: HTMLAttributes<HTMLPreElement>) {
  const [copied, setCopied] = useState(false);
  const mounted = useSyncExternalStore(
    subscribeToHydration,
    () => true,
    () => false,
  );
  const { resolvedTheme } = useTheme();
  const code = useMemo(
    () => extractText(props.children).trimEnd(),
    [props.children],
  );
  const language = useMemo(() => {
    const child = props.children as
      | { props?: { className?: string } }
      | undefined;
    const match = /language-([\w-]+)/.exec(child?.props?.className ?? "");
    return match?.[1] ?? "text";
  }, [props.children]);

  async function copyCode() {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }

  if (!mounted) {
    return (
      <div className="my-6 h-40 w-full animate-pulse border border-border bg-muted/45" />
    );
  }

  const isDark = resolvedTheme === "dark";

  return (
    <figure className="group my-6 max-w-full overflow-hidden border border-border bg-card/35">
      <figcaption className="flex min-h-9 items-center justify-between border-b border-border bg-muted/30 px-3 sm:px-4">
        <span className="truncate font-mono text-[10px] uppercase tracking-[0.13em] text-muted-foreground">
          {language}
        </span>
        <button
          type="button"
          onClick={copyCode}
          aria-label={copied ? "Copied code" : "Copy code"}
          className="inline-flex h-7 items-center gap-1.5 px-2 text-[11px] font-medium text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
        >
          {copied ? (
            <>
              <Check className="size-3.5" />
              Copied
            </>
          ) : (
            <>
              <Copy className="size-3.5" />
              Copy
            </>
          )}
        </button>
      </figcaption>
      <div className="max-w-full overflow-x-auto scrollbar-thin">
        <SyntaxHighlighter
          language={language}
          style={isDark ? vscDarkPlus : vs}
          PreTag="div"
          wrapLongLines={false}
          customStyle={{
            margin: 0,
            minWidth: "max-content",
            padding: "1rem",
            fontSize: "0.8125rem",
            lineHeight: "1.55",
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
      </div>
    </figure>
  );
}
