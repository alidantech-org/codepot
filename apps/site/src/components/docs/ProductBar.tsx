import Link from "next/link";
import { ExternalLink, Package, Terminal } from "lucide-react";

import { getAvailableLinks, getProductById } from "@/lib/ecosystem";

export function ProductBar({ productId }: { productId: string }) {
  const product = getProductById(productId);
  if (!product) return null;

  const links = getAvailableLinks(product);

  return (
    <section className="mb-8 border-y border-border bg-card/35 px-4 py-5 sm:px-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-[10px] uppercase tracking-[0.15em] text-primary">
              {product.kind}
            </span>
            <span className="h-1 w-1 rounded-full bg-border" aria-hidden="true" />
            <span className="text-xs text-muted-foreground">{product.status}</span>
            <span className="border-l border-border pl-2 text-xs text-muted-foreground">
              {product.availability}
            </span>
          </div>
          <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">
            {product.role}
          </p>
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          {links.map((link) => (
            <a
              key={`${product.id}-${link.label}`}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-8 items-center gap-1.5 border border-border bg-background px-2.5 text-xs font-medium text-foreground transition-colors hover:border-primary/35 hover:bg-primary/5"
            >
              {link.kind === "npm" || link.kind === "pypi" || link.kind === "package" ? (
                <Package className="h-3.5 w-3.5" />
              ) : (
                <ExternalLink className="h-3.5 w-3.5" />
              )}
              {link.label}
            </a>
          ))}
          <Link
            href="/docs/package-links"
            className="inline-flex h-8 items-center gap-1.5 border border-border px-2.5 text-xs text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            All links
          </Link>
        </div>
      </div>

      {(product.install || product.command) && (
        <div className="mt-4 flex min-w-0 items-center gap-2 border-t border-border pt-4">
          <Terminal className="h-3.5 w-3.5 shrink-0 text-primary" />
          <code className="min-w-0 overflow-x-auto whitespace-nowrap font-mono text-xs text-foreground scrollbar-thin">
            {product.install ?? product.command}
          </code>
        </div>
      )}
    </section>
  );
}
