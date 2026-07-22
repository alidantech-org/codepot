import type { ReactNode } from 'react';
import Link from 'next/link';
import { ArrowLeft, ArrowRight } from 'lucide-react';

import type { DocRecord, NavigationSection } from '@/lib/docs';

export function DocsShell({
  navigation,
  activeSlug,
  previous,
  next,
  children,
}: {
  readonly navigation: readonly NavigationSection[];
  readonly activeSlug: string;
  readonly previous?: DocRecord;
  readonly next?: DocRecord;
  readonly children: ReactNode;
}) {
  return (
    <div className="docs-layout">
      <aside className="docs-sidebar" aria-label="Documentation navigation">
        <div className="docs-sidebar__sticky">
          {navigation.map((section) => (
            <section key={section.title} className="docs-nav-section">
              <h2>{section.title}</h2>
              <ul>
                {section.items.map((item) => (
                  <li key={item.slug}>
                    <Link
                      aria-current={item.slug === activeSlug ? 'page' : undefined}
                      className={item.slug === activeSlug ? 'is-active' : undefined}
                      href={`/docs/${item.slug}`}
                    >
                      {item.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </aside>
      <main className="docs-main">
        <article className="doc-prose">{children}</article>
        <nav className="docs-pagination" aria-label="Previous and next pages">
          {previous ? (
            <Link href={`/docs/${previous.slug}`}>
              <ArrowLeft size={16} />
              <span><small>Previous</small>{previous.metadata.title}</span>
            </Link>
          ) : <span />}
          {next ? (
            <Link className="docs-pagination__next" href={`/docs/${next.slug}`}>
              <span><small>Next</small>{next.metadata.title}</span>
              <ArrowRight size={16} />
            </Link>
          ) : <span />}
        </nav>
      </main>
    </div>
  );
}
