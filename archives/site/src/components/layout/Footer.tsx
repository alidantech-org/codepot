export function Footer() {
  return (
    <footer className="relative z-10 border-t border-border py-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-4 px-6 text-xs text-muted-foreground sm:flex-row">
        <span> {new Date().getFullYear()} Codepurify · MIT License</span>
        <div className="flex gap-5">
          <a
            href="https://github.com/alidantech-org/codepurify"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-foreground"
          >
            GitHub
          </a>
          <a href="/docs" className="transition-colors hover:text-foreground">
            Docs
          </a>
          <a
            href="https://www.npmjs.com/package/codepurify"
            target="_blank"
            rel="noopener noreferrer"
            className="transition-colors hover:text-foreground"
          >
            npm
          </a>
        </div>
      </div>
    </footer>
  );
}
