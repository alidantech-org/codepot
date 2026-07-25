import Image from "next/image";
import Link from "next/link";

import { ecosystem, getAvailableLinks, getProductById } from "@/lib/ecosystem";
import Logo from "./Logo";

const footerGroups = [
  {
    title: "Codepot",
    links: [
      ["Overview", "/docs/overview"],
      ["Getting started", "/docs/getting-started"],
      ["Ecosystem", "/docs/ecosystem"],
      ["Architecture", "/docs/architecture"],
      ["Choose a workflow", "/docs/choose-workflow"],
    ],
  },
  {
    title: "Packages",
    links: [
      ["codepot-openapi", "/docs/codepot-openapi"],
      ["codepotg", "/docs/codepotg"],
      ["codepotx", "/docs/codepotx"],
      ["codepotx-cli", "/docs/codepotx-cli"],
      ["Package links", "/docs/package-links"],
    ],
  },
  {
    title: "Platform",
    links: [
      ["Codepot Lang", "/docs/codepot-lang"],
      ["codepot CLI", "/docs/codepot-cli"],
      ["Codepot LSP", "/docs/codepot-lsp"],
      ["Language extension", "/docs/codepot-extension"],
      ["Web and MCP", "/docs/codepot-web-mcp"],
    ],
  },
  {
    title: "Learn",
    links: [
      ["Guides", "/docs/guides"],
      ["Typed intent", "/docs/typed-intent"],
      ["Template packs", "/docs/template-packs"],
      ["Generation safety", "/docs/generation-safety"],
      ["Contributing", "/docs/repository-structure"],
    ],
  },
] as const;

export function Footer() {
  const openapi = getProductById("codepot-openapi");
  const codepotg = getProductById("codepotg");
  const registryLinks = [openapi, codepotg]
    .flatMap((product) => (product ? getAvailableLinks(product) : []))
    .filter((link) => link.kind === "npm" || link.kind === "pypi");

  return (
    <footer className="relative overflow-hidden border-t border-border bg-[linear-gradient(180deg,color-mix(in_srgb,var(--card)_72%,transparent),var(--card))]">
      <div
        aria-hidden="true"
        className="absolute -left-24 top-8 h-72 w-72 rounded-full bg-primary/8 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="absolute -right-24 bottom-0 h-64 w-64 rounded-full bg-accent/8 blur-3xl"
      />

      <div className="relative mx-auto  px-6 py-12">
        <div className="grid gap-12 lg:grid-cols-[1.4fr_3fr]">
          <div>
            <Logo />

            <p className="mt-5 max-w-sm text-sm leading-7 text-muted-foreground">
              {ecosystem.project.tagline}
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              <a
                href={ecosystem.project.github}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-full border border-border bg-background/75 px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:border-primary/35 hover:bg-card-muted"
              >
                GitHub
              </a>
              {registryLinks.map((link) => (
                <a
                  key={link.url}
                  href={link.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-full border border-border bg-background/75 px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:border-primary/35 hover:bg-card-muted"
                >
                  {link.label}
                </a>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-x-8 gap-y-10 sm:grid-cols-4">
            {footerGroups.map((group) => (
              <div key={group.title}>
                <h2 className="text-xs font-semibold uppercase tracking-[0.16em] text-foreground">
                  {group.title}
                </h2>
                <ul className="mt-4 space-y-3">
                  {group.links.map(([label, href]) => (
                    <li key={href}>
                      <Link
                        href={href}
                        className="text-sm text-muted-foreground transition-colors hover:text-primary"
                      >
                        {label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 flex flex-col gap-3 border-t border-border pt-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
          <span>
            {new Date().getFullYear()} Codepot · {ecosystem.project.license}{" "}
            License
          </span>
          <span>
            Typed software intent · reusable templates · safe generation
          </span>
        </div>
      </div>
    </footer>
  );
}
