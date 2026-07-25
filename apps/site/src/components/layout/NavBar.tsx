"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { ArrowRight, FileText, Hash, Menu, Search, X } from "lucide-react";
import {
  Fragment,
  useEffect,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
} from "react";

import { GitHubIcon } from "@/components/icons/GitHubIcon";
import { MobileSidebar } from "@/components/layout/MobileSidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { DOC_SEARCH_INDEX } from "@/generated/docs";

import Logo from "./Logo";

const primaryLinks = [
  { label: "Docs", href: "/docs" },
  { label: "Packages", href: "/docs/packages" },
  { label: "Guides", href: "/docs/guides" },
  { label: "Codepot Lang", href: "/docs/codepot-lang" },
] as const;

const MAX_RESULTS = 12;
const SEARCH_DEBOUNCE_MS = 150;

type SearchRecord = (typeof DOC_SEARCH_INDEX)[number];

interface RankedResult {
  item: SearchRecord;
  score: number;
}

function normalize(value: string): string {
  return value
    .normalize("NFKD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9+#./_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function scoreRecord(item: SearchRecord, query: string): number {
  const normalizedQuery = normalize(query);
  if (!normalizedQuery) {
    if (item.kind !== "page") return -1;
    if (item.path === "") return 120;
    if (item.path === "packages") return 110;
    if (item.package && item.path === `packages/${item.package}`) return 100;
    return 20;
  }

  const tokens = normalizedQuery.split(" ").filter(Boolean);
  const title = normalize(item.title);
  const pageTitle = normalize(item.pageTitle);
  const section = normalize(item.section);
  const packageName = normalize(item.package ?? "");
  const searchText = item.searchText;

  if (!tokens.every((token) => searchText.includes(token))) return -1;

  let score = item.kind === "heading" ? 14 : 10;
  if (title === normalizedQuery) score += 160;
  else if (title.startsWith(normalizedQuery)) score += 110;
  else if (title.includes(normalizedQuery)) score += 76;

  if (packageName === normalizedQuery) score += 145;
  else if (packageName.startsWith(normalizedQuery)) score += 80;
  else if (packageName.includes(normalizedQuery)) score += 42;

  if (pageTitle === normalizedQuery) score += 100;
  else if (pageTitle.startsWith(normalizedQuery)) score += 62;
  else if (pageTitle.includes(normalizedQuery)) score += 36;

  if (section.includes(normalizedQuery)) score += 18;
  if (searchText.includes(normalizedQuery)) score += 26;

  for (const token of tokens) {
    if (title === token) score += 38;
    else if (title.startsWith(token)) score += 25;
    else if (title.includes(token)) score += 16;

    if (packageName === token) score += 34;
    if (pageTitle.startsWith(token)) score += 10;
    if (item.description && normalize(item.description).includes(token)) score += 6;
  }

  return score;
}

function rankResults(query: string): RankedResult[] {
  return DOC_SEARCH_INDEX.map((item) => ({
    item,
    score: scoreRecord(item, query),
  }))
    .filter((result) => result.score >= 0)
    .sort(
      (left, right) =>
        right.score - left.score || left.item.title.localeCompare(right.item.title),
    )
    .slice(0, MAX_RESULTS);
}

function Highlight({ text, query }: { text: string; query: string }) {
  const tokens = normalize(query)
    .split(" ")
    .filter((token) => token.length > 1);
  if (!tokens.length) return text;

  const pattern = new RegExp(
    `(${tokens
      .map((token) => token.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
      .join("|")})`,
    "gi",
  );
  const parts = text.split(pattern);

  return (
    <>
      {parts.map((part, index) =>
        tokens.some((token) => normalize(part) === token) ? (
          <mark
            key={`${part}-${index}`}
            className="bg-primary/15 px-0.5 text-inherit"
          >
            {part}
          </mark>
        ) : (
          <Fragment key={`${part}-${index}`}>{part}</Fragment>
        ),
      )}
    </>
  );
}

function ResultContext({ item }: { item: SearchRecord }) {
  const labels = item.breadcrumbs
    .filter((crumb) => crumb.path !== "")
    .map((crumb) => crumb.title);

  return (
    <span className="mt-1.5 flex min-w-0 items-center gap-1.5 overflow-hidden font-mono text-[10px] uppercase tracking-wide text-muted-foreground/75">
      <span className="shrink-0">{item.section}</span>
      {labels.map((label) => (
        <Fragment key={label}>
          <span aria-hidden="true" className="text-border">
            /
          </span>
          <span className="truncate">{label}</span>
        </Fragment>
      ))}
    </span>
  );
}

export function NavBar() {
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const [searchOpen, setSearchOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    const timer = window.setTimeout(
      () => setDebouncedQuery(query),
      SEARCH_DEBOUNCE_MS,
    );
    return () => window.clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    function handleShortcut(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
    }

    window.addEventListener("keydown", handleShortcut);
    return () => window.removeEventListener("keydown", handleShortcut);
  }, []);

  useEffect(() => {
    if (!searchOpen) return;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.requestAnimationFrame(() => inputRef.current?.focus());
    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [searchOpen]);

  const rankedResults = useMemo(
    () => rankResults(debouncedQuery),
    [debouncedQuery],
  );
  const results = rankedResults.map((result) => result.item);
  const isSearching = query !== debouncedQuery;

  useEffect(() => {
    setSelectedIndex(0);
  }, [debouncedQuery]);

  useEffect(() => {
    const selected = resultsRef.current?.querySelector<HTMLElement>(
      `[data-search-index="${selectedIndex}"]`,
    );
    selected?.scrollIntoView({ block: "nearest" });
  }, [selectedIndex]);

  function closeSearch() {
    setSearchOpen(false);
    setQuery("");
    setDebouncedQuery("");
    setSelectedIndex(0);
  }

  function navigateTo(href: string) {
    closeSearch();
    router.push(href);
  }

  function handleSearchKeyDown(event: ReactKeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      event.preventDefault();
      closeSearch();
      return;
    }

    if (event.key === "ArrowDown") {
      event.preventDefault();
      setSelectedIndex((current) =>
        results.length ? (current + 1) % results.length : 0,
      );
      return;
    }

    if (event.key === "ArrowUp") {
      event.preventDefault();
      setSelectedIndex((current) =>
        results.length ? (current - 1 + results.length) % results.length : 0,
      );
      return;
    }

    if (event.key === "Enter" && results[selectedIndex]) {
      event.preventDefault();
      navigateTo(results[selectedIndex].href);
    }
  }

  return (
    <>
      <MobileSidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <nav className="sticky top-0 z-20 border-b border-border bg-background/82 backdrop-blur-xl">
        <div className="mx-auto flex h-15 items-center justify-between gap-3 px-2 md:px-6">
          <div className="flex min-w-0 items-center gap-3 lg:gap-8">
            <Logo />
            <div className="hidden items-center gap-1 text-sm text-muted-foreground lg:flex">
              {primaryLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className="rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground"
                >
                  {link.label}
                </Link>
              ))}
              <a
                href="https://github.com/alidantech-org/codepot"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 rounded-xl px-3 py-2 transition-colors hover:bg-card-muted hover:text-foreground"
              >
                <GitHubIcon />
                GitHub
              </a>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => setSearchOpen(true)}
              aria-label="Search documentation"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground sm:w-auto md:border md:border-border md:bg-card/80 md:px-3 lg:min-w-52 lg:justify-start"
            >
              <Search className="h-5 w-5 shrink-0" />
              <span className="ml-2 hidden text-sm sm:inline">Search docs</span>
              <kbd className="ml-auto hidden rounded-md border border-border bg-background px-1.5 py-0.5 font-mono text-[10px] text-muted-foreground lg:inline-flex">
                Ctrl K
              </kbd>
            </button>
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Open navigation menu"
              className="inline-flex h-10 w-10 items-center justify-center rounded-xl text-muted-foreground transition-colors hover:bg-card-muted hover:text-foreground lg:hidden"
            >
              <Menu className="h-7 w-7" />
            </button>
          </div>
        </div>
      </nav>

      {searchOpen && (
        <div
          className="fixed inset-0 z-[1000] bg-background/72 px-3 py-4 backdrop-blur-md sm:px-6"
          onMouseDown={closeSearch}
          role="presentation"
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Search Codepot documentation"
            className="mx-auto mt-[7vh] flex max-h-[86vh] w-full max-w-2xl flex-col overflow-hidden border border-border bg-card shadow-[0_24px_90px_rgba(0,0,0,0.24)] sm:mt-[11vh]"
            onMouseDown={(event) => event.stopPropagation()}
          >
            <div className="flex min-h-14 items-center border-b border-border px-4 sm:px-5">
              <Search className="mr-3 h-4 w-4 shrink-0 text-muted-foreground" />
              <input
                ref={inputRef}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                onKeyDown={handleSearchKeyDown}
                placeholder="Search packages, pages, headings, concepts, and commands…"
                className="h-14 min-w-0 flex-1 bg-transparent text-[15px] text-foreground outline-none placeholder:text-muted-foreground"
                autoComplete="off"
                spellCheck={false}
              />
              {query ? (
                <button
                  type="button"
                  onClick={() => setQuery("")}
                  className="inline-flex h-8 w-8 items-center justify-center text-muted-foreground hover:bg-card-muted hover:text-foreground"
                  aria-label="Clear search"
                >
                  <X className="h-4 w-4" />
                </button>
              ) : (
                <kbd className="border border-border bg-background px-2 py-1 font-mono text-[10px] text-muted-foreground">
                  ESC
                </kbd>
              )}
            </div>

            <div className="flex min-h-0 flex-1 flex-col">
              <div className="flex items-center justify-between border-b border-border/70 px-4 py-2 text-[11px] text-muted-foreground sm:px-5">
                <span>
                  {debouncedQuery
                    ? `Results for “${debouncedQuery}”`
                    : "Suggested documentation"}
                </span>
                <span>
                  {isSearching
                    ? "Searching…"
                    : `${results.length} result${results.length === 1 ? "" : "s"}`}
                </span>
              </div>

              <div
                ref={resultsRef}
                className="min-h-0 flex-1 overflow-y-auto overscroll-contain py-2 scrollbar-thin"
              >
                {results.length ? (
                  <div
                    role="listbox"
                    aria-label="Search results"
                    className="px-2 sm:px-3"
                  >
                    {results.map((item, index) => {
                      const selected = index === selectedIndex;
                      return (
                        <button
                          key={item.id}
                          type="button"
                          role="option"
                          aria-selected={selected}
                          data-search-index={index}
                          onMouseEnter={() => setSelectedIndex(index)}
                          onClick={() => navigateTo(item.href)}
                          className={`group flex w-full items-start gap-3 border-l-2 px-3 py-3 text-left transition-colors sm:px-4 ${
                            selected
                              ? "border-primary bg-primary/8"
                              : "border-transparent hover:border-border hover:bg-card-muted/60"
                          }`}
                        >
                          <span
                            className={`mt-0.5 inline-flex h-7 w-7 shrink-0 items-center justify-center border ${
                              selected
                                ? "border-primary/35 bg-primary/10 text-primary"
                                : "border-border bg-background text-muted-foreground"
                            }`}
                          >
                            {item.kind === "heading" ? (
                              <Hash className="h-3.5 w-3.5" />
                            ) : (
                              <FileText className="h-3.5 w-3.5" />
                            )}
                          </span>
                          <span className="min-w-0 flex-1">
                            <span className="flex flex-wrap items-center gap-x-2 gap-y-1">
                              <span className="font-medium text-foreground">
                                <Highlight
                                  text={item.title}
                                  query={debouncedQuery}
                                />
                              </span>
                              {item.kind === "heading" && (
                                <span className="text-xs text-muted-foreground">
                                  in {item.pageTitle}
                                </span>
                              )}
                              {item.package && (
                                <span className="border border-primary/20 bg-primary/5 px-1.5 py-0.5 font-mono text-[9px] text-primary">
                                  {item.package}
                                </span>
                              )}
                            </span>
                            {item.snippet && (
                              <span className="mt-1 line-clamp-2 block text-xs leading-5 text-muted-foreground">
                                <Highlight
                                  text={item.snippet}
                                  query={debouncedQuery}
                                />
                              </span>
                            )}
                            <ResultContext item={item} />
                          </span>
                          <ArrowRight
                            className={`mt-1 h-4 w-4 shrink-0 transition-all ${
                              selected
                                ? "translate-x-0 opacity-100 text-primary"
                                : "-translate-x-1 opacity-0 text-muted-foreground group-hover:translate-x-0 group-hover:opacity-100"
                            }`}
                          />
                        </button>
                      );
                    })}
                  </div>
                ) : (
                  <div className="grid min-h-52 place-items-center px-6 py-12 text-center">
                    <div>
                      <Search className="mx-auto h-7 w-7 text-muted-foreground/60" />
                      <p className="mt-3 text-sm font-medium text-foreground">
                        No documentation found
                      </p>
                      <p className="mt-1 text-xs leading-5 text-muted-foreground">
                        Try a package name, command, heading, or shorter phrase.
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="hidden items-center justify-between border-t border-border bg-background/50 px-4 py-2 text-[10px] text-muted-foreground sm:flex">
              <span>Searches generated pages, package trees, and TOC headings</span>
              <span className="flex items-center gap-3 font-mono">
                <span>↑↓ Navigate</span>
                <span>↵ Open</span>
                <span>Esc Close</span>
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
