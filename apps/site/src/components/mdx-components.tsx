import type { ComponentPropsWithoutRef, ReactElement, ReactNode } from 'react';
import Link from 'next/link';
import { codeToHtml } from 'shiki';
import type { MDXComponents } from '@mdx-js/react';

function HeadingAnchor({ id, children }: { readonly id?: string; readonly children: ReactNode }) {
  if (!id) return children;
  return <Link className="heading-anchor" href={`#${id}`}>{children}</Link>;
}

async function CodeBlock({ children }: { readonly children?: ReactNode }) {
  const child = children as ReactElement<{ readonly children?: ReactNode; readonly className?: string }> | undefined;
  const language = child?.props.className?.replace('language-', '') || 'text';
  const source = String(child?.props.children ?? '').replace(/\n$/, '');
  const html = await codeToHtml(source, {
    lang: language,
    themes: {
      light: 'github-light-default',
      dark: 'github-dark-default',
    },
    defaultColor: false,
  });
  return <div className="code-frame" dangerouslySetInnerHTML={{ __html: html }} />;
}

function SmartLink({ href = '', children, ...props }: ComponentPropsWithoutRef<'a'>) {
  if (href.startsWith('/')) return <Link href={href} {...props}>{children}</Link>;
  return <a href={href} rel="noreferrer" target={href.startsWith('http') ? '_blank' : undefined} {...props}>{children}</a>;
}

export const mdxComponents: MDXComponents = {
  h1: ({ children, id, ...props }) => <h1 id={id} {...props}><HeadingAnchor id={id}>{children}</HeadingAnchor></h1>,
  h2: ({ children, id, ...props }) => <h2 id={id} {...props}><HeadingAnchor id={id}>{children}</HeadingAnchor></h2>,
  h3: ({ children, id, ...props }) => <h3 id={id} {...props}><HeadingAnchor id={id}>{children}</HeadingAnchor></h3>,
  a: SmartLink,
  pre: CodeBlock,
  code: ({ children, ...props }) => <code {...props}>{children}</code>,
  table: ({ children, ...props }) => <div className="table-scroll"><table {...props}>{children}</table></div>,
  blockquote: ({ children, ...props }) => <blockquote className="doc-callout" {...props}>{children}</blockquote>,
};
