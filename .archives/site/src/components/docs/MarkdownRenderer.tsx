// src/components/docs/MarkdownRenderer.tsx

import { MDXRemote } from "next-mdx-remote/rsc";
import Link from "next/link";
import remarkGfm from "remark-gfm";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import { CodeBlock } from "./CodeBlock";

type MarkdownRendererProps = {
  content: string;
};

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  return (
    <div className="max-w-none text-foreground">
      <MDXRemote
        source={content}
        options={{
          mdxOptions: {
            remarkPlugins: [remarkGfm],
            rehypePlugins: [
              rehypeSlug,
              [
                rehypeAutolinkHeadings,
                {
                  behavior: "append",
                  properties: {
                    className: ["anchor"],
                    ariaLabel: "Link to section",
                  },
                },
              ],
              // [
              //   rehypePrettyCode,
              //   {
              //     theme: {
              //       light: "github-light",
              //       dark: "github-dark-dimmed",
              //     },
              //     keepBackground: false,
              //   },
              // ],
            ],
          },
        }}
        components={{
          h1: ({ children }) => (
            <h1 className="mb-6 mt-2 scroll-mt-24 text-3xl font-bold tracking-tight text-foreground">
              {children}
            </h1>
          ),

          h2: ({ children, id }) => (
            <h2
              id={id}
              className="mb-4 mt-12 scroll-mt-24 border-b border-border pb-2 text-xl font-semibold tracking-tight text-foreground"
            >
              {children}
            </h2>
          ),

          h3: ({ children, id }) => (
            <h3
              id={id}
              className="mb-3 mt-8 scroll-mt-24 text-lg font-semibold tracking-tight text-foreground"
            >
              {children}
            </h3>
          ),

          h4: ({ children, id }) => (
            <h4
              id={id}
              className="mb-2 mt-6 scroll-mt-24 text-base font-semibold text-foreground"
            >
              {children}
            </h4>
          ),

          p: ({ children }) => (
            <p className="my-4 leading-7 text-muted-foreground">{children}</p>
          ),

          a: ({ href = "", children, ...props }) => {
            const isInternal = href.startsWith("/");
            const isHash = href.startsWith("#");

            if (isInternal) {
              return (
                <Link
                  href={href}
                  className="font-medium text-primary underline underline-offset-4 transition-colors hover:text-primary/80"
                >
                  {children}
                </Link>
              );
            }

            return (
              <a
                href={href}
                target={isHash ? undefined : "_blank"}
                rel={isHash ? undefined : "noopener noreferrer"}
                className="font-medium text-primary underline underline-offset-4 transition-colors hover:text-primary/80"
                {...props}
              >
                {children}
              </a>
            );
          },

          ul: ({ children }) => (
            <ul className="my-5 ml-6 list-disc space-y-2 text-muted-foreground marker:text-muted-foreground/50">
              {children}
            </ul>
          ),

          ol: ({ children }) => (
            <ol className="my-5 ml-6 list-decimal space-y-2 text-muted-foreground marker:text-muted-foreground/50">
              {children}
            </ol>
          ),

          li: ({ children }) => <li className="leading-7">{children}</li>,

          code: ({ className, children, ...props }) => {
            const isBlock = className?.startsWith("language-");

            if (isBlock) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }

            return (
              <code
                className="rounded-md border border-border bg-muted px-1.5 py-0.5 font-mono text-[0.8em] text-foreground"
                {...props}
              >
                {children}
              </code>
            );
          },

          pre: CodeBlock,

          blockquote: ({ children }) => (
            <blockquote className="my-6 rounded-r-lg border-l-4 border-primary bg-muted/40 px-5 py-3 italic text-muted-foreground">
              {children}
            </blockquote>
          ),

          hr: () => <hr className="my-8 border-border" />,

          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">
              {children}
            </strong>
          ),

          em: ({ children }) => (
            <em className="italic text-muted-foreground">{children}</em>
          ),

          table: ({ children }) => (
            <div className="my-6 overflow-x-auto rounded-xl border border-border">
              <table className="w-full border-collapse text-sm">
                {children}
              </table>
            </div>
          ),

          thead: ({ children }) => (
            <thead className="bg-muted/50">{children}</thead>
          ),

          th: ({ children }) => (
            <th className="px-4 py-3 text-left font-medium text-foreground">
              {children}
            </th>
          ),

          td: ({ children }) => (
            <td className="border-t border-border px-4 py-3 text-muted-foreground">
              {children}
            </td>
          ),
        }}
      />
    </div>
  );
}
