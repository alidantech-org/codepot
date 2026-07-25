import Link from "next/link";
import { ExternalLink, Package, Terminal } from "lucide-react";

import { getAvailableLinks, getProductById } from "@/lib/ecosystem";

export function ProductBar({ productId }: { productId: string }) {
  const product = getProductById(productId);
  if (!product) return null;

  const links = getAvailableLinks(product);

  return (
    <section className="mb-8 rounded-2xl border border-border bg-card/70 p-5 shadow-sm">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-primary/25 bg-primary/10 px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-primary">
              {product.status}
            </span>
            <span className="rounded-full border border-border bg-background px-2.5 py-1 text-[11px] text-muted-foreground">
              {product.availability}
            </span>
          </div>
          <p className="mt-3 text-sm leading-6 text-muted-foreground">{product.role}</p>
        </div>

        <div className="flex shrink-0 flex-wrap gap-2">
          {links.map((link) => (
            <a
              key={`${product.id}-${link.label}`}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-9 items-center gap-2 rounded-xl border border-border bg-background px-3 text-xs font-medium text-foreground transition-colors hover:bg-card-muted"
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
            className="inline-flex h-9 items-center gap-2 rounded-xl border border-border px-3 text-xs text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground"
          >
            <ExternalLink className="h-3.5 w-3.5" />
            All links
          </Link>
        </div>
      </div>

      {(product.install || product.command) && (
        <div className="mt-5 flex flex-col gap-2 border-t border-border pt-4 sm:flex-row sm:items-center">
          <Terminal className="h-4 w-4 shrink-0 text-primary" />
          <code className="overflow-x-auto font-mono text-xs text-foreground">
            {product.install ?? product.command}
          </code>
        </div>
      )}
    </section>
  );
}
