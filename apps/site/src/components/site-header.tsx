import Link from 'next/link';
import { Box, Github, TerminalSquare } from 'lucide-react';

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-header__inner">
        <Link className="brand" href="/">
          <span className="brand__mark"><Box aria-hidden="true" size={18} /></span>
          <span>Codepot</span>
        </Link>
        <nav aria-label="Primary navigation" className="site-nav">
          <Link href="/docs/getting-started">Docs</Link>
          <Link href="/docs/template-variables">Template variables</Link>
          <Link href="/docs/generation-safety">Safety</Link>
        </nav>
        <div className="site-actions">
          <Link className="icon-link" href="/docs/cli" aria-label="CLI documentation">
            <TerminalSquare size={18} />
          </Link>
          <a
            className="icon-link"
            href="https://github.com/alidantech-org/codepot"
            aria-label="Codepot on GitHub"
            rel="noreferrer"
            target="_blank"
          >
            <Github size={18} />
          </a>
        </div>
      </div>
    </header>
  );
}
