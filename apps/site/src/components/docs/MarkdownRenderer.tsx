import Link from "next/link";
import { MDXRemote } from "next-mdx-remote/rsc";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypeSlug from "rehype-slug";
import remarkGfm from "remark-gfm";

import { CodeBlock } from "@/components/docs/CodeBlock";

export function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="max-w-none text-[15px] text-foreground sm:text-base">
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
            ],
          },
        }}
        components={{
          h1: ({ children }) => (
            <h1 className="mb-5 mt-1 max-w-4xl scroll-mt-24 text-3xl font-bold tracking-[-0.025em] text-foreground sm:text-4xl">
              {children}
            </h1>
          ),
          h2: ({ children, id }) => (
            <h2
              id={id}
              className="mb-4 mt-11 max-w-4xl scroll-mt-24 border-b border-border pb-2.5 text-xl font-semibold tracking-tight text-foreground sm:mt-13 sm:text-2xl"
            >
              {children}
            </h2>
          ),
          h3: ({ children, id }) => (
            <h3
              id={id}
              className="mb-3 mt-8 max-w-4xl scroll-mt-24 text-lg font-semibold tracking-tight text-foreground sm:text-xl"
            >
              {children}
            </h3>
          ),
          h4: ({ children, id }) => (
            <h4
              id={id}
              className="mb-2 mt-6 max-w-4xl scroll-mt-24 text-base font-semibold text-foreground"
            >
              {children}
            </h4>
          ),
          p: ({ children }) => (
            <p className="my-4 max-w-[52rem] leading-7 text-muted-foreground">
              {children}
            </p>
          ),
          a: ({ href = "", children, ...props }) => {
            if (href.startsWith("/")) {
              return (
                <Link
                  href={href}
                  className="font-medium text-primary underline decoration-primary/35 underline-offset-4 transition-colors hover:text-primary/80"
                >
                  {children}
                </Link>
              );
            }
            const isHash = href.startsWith("#");
            return (
              <a
                href={href}
                target={isHash ? undefined : "_blank"}
                rel={isHash ? undefined : "noopener noreferrer"}
                className="font-medium text-primary underline decoration-primary/35 underline-offset-4 transition-colors hover:text-primary/80"
                {...props}
              >
                {children}
              </a>
            );
          },
          ul: ({ children }) => (
            <ul className="my-5 ml-5 max-w-[50rem] list-disc space-y-1.5 text-muted-foreground marker:text-primary/55 sm:ml-6">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="my-5 ml-5 max-w-[50rem] list-decimal space-y-1.5 text-muted-foreground marker:font-medium marker:text-primary/65 sm:ml-6">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="pl-1 leading-7">{children}</li>,
          code: ({ className, children, ...props }) => {
            if (className?.startsWith("language-")) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code
                className="border border-border bg-muted px-1.5 py-0.5 font-mono text-[0.82em] text-foreground"
                {...props}
              >
                {children}
              </code>
            );
          },
          pre: CodeBlock,
          blockquote: ({ children }) => (
            <blockquote className="my-6 max-w-[52rem] border-l-2 border-primary bg-primary/5 px-5 py-3 text-muted-foreground">
              {children}
            </blockquote>
          ),
          hr: () => <hr className="my-9 border-border" />,
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-muted-foreground">{children}</em>
          ),
          table: ({ children }) => (
            <div className="my-6 max-w-full overflow-x-auto border border-border scrollbar-thin">
              <table className="w-full min-w-[38rem] border-collapse text-sm">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => <thead className="bg-muted/45">{children}</thead>,
          th: ({ children }) => (
            <th className="border-b border-border px-4 py-3 text-left font-semibold text-foreground">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border-t border-border px-4 py-3 align-top leading-6 text-muted-foreground">
              {children}
            </td>
          ),
        }}
      />
    </div>
  );
}
