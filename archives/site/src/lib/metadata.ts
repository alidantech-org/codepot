import { Metadata } from "next";

export const siteConfig = {
  name: "codepot",
  description:
    "Semantic metadata inference engine and template compiler. Define facts once, generate infinite architecture outputs.",
  url: "https://codepot.dev",
  ogImage: "https://codepot.dev/og-image.png",
  links: {
    twitter: "https://twitter.com/codepot",
    github: "https://github.com/alidantech-org/codepot",
    docs: "https://github.com/alidantech-org/codepot#readme",
    npm: "https://www.npmjs.com/package/codepot",
  },
};

export type SiteConfig = typeof siteConfig;

export function generateMetadata(): Metadata {
  const title = "codepot - Semantic Metadata Inference Engine";
  const description =
    "Define facts once, generate infinite architecture outputs. Strongly typed TypeScript configs, semantic metadata inference, and template compilation for modern development.";

  return {
    title: {
      default: title,
      template: `%s | ${siteConfig.name}`,
    },
    description,
    metadataBase: new URL(siteConfig.url),
    keywords: [
      "semantic metadata",
      "inference engine",
      "template compiler",
      "TypeScript",
      "code generation",
      "ORM",
      "entity framework",
      "API generation",
      "schema generation",
      "backend development",
      "frontend development",
      "full-stack",
      "development tools",
      "automation",
      "type-safe",
      "metadata-driven",
      "code generation",
      "template engine",
      "codepot",
      "GraphQL",
      "OpenAPI",
      "Zod",
      "Pydantic",
      "React forms",
      "admin panels",
      "SDK generation",
      "repository pattern",
      "DTO generation",
      "validation layers",
      "query builders",
      "relation graphs",
      "workflows",
      "state machines",
      "enum transitions",
      "framework agnostic",
      "MIT license",
      "open source",
    ],
    authors: [{ name: "AliDanTech", url: siteConfig.links.github }],
    creator: "AliDanTech",
    publisher: "AliDanTech",
    formatDetection: {
      email: false,
      address: false,
      telephone: false,
    },
    openGraph: {
      type: "website",
      locale: "en_US",
      url: siteConfig.url,
      title,
      description,
      siteName: siteConfig.name,
      images: [
        {
          url: siteConfig.ogImage,
          width: 1200,
          height: 630,
          alt: "codepot - Semantic Metadata Inference Engine",
        },
      ],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [siteConfig.ogImage],
      creator: "@codepot",
      site: "@codepot",
    },
    robots: {
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        "max-video-preview": -1,
        "max-image-preview": "large",
        "max-snippet": -1,
      },
    },
    verification: {
      google: "your-google-verification-code",
      yandex: "your-yandex-verification-code",
      yahoo: "your-yahoo-verification-code",
    },
  };
}

export function generateStructuredData() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "codepot",
    description:
      "Semantic metadata inference engine and template compiler. Define facts once, generate infinite architecture outputs.",
    url: siteConfig.url,
    applicationCategory: "DeveloperApplication",
    operatingSystem: "Any",
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
      availability: "https://schema.org/InStock",
    },
    author: {
      "@type": "Organization",
      name: "AliDanTech",
      url: siteConfig.links.github,
    },
    publisher: {
      "@type": "Organization",
      name: "AliDanTech",
      url: siteConfig.links.github,
    },
    license: "https://opensource.org/licenses/MIT",
    downloadUrl: siteConfig.links.npm,
    installUrl: siteConfig.links.docs,
    screenshot: siteConfig.ogImage,
    featureList: [
      "Strongly typed TypeScript configs",
      "Semantic metadata inference",
      "codepot-based generation",
      "Framework agnostic",
      "Runtime metadata compilation",
      "Query/mutation capability inference",
      "Typed enum transitions & workflows",
      "Relation graph inference",
      "JSON-safe normalized manifests",
      "Extensible template ecosystem",
    ],
    programmingLanguage: "TypeScript",
    runtimePlatform: "Node.js",
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: "5.0",
      ratingCount: "100",
    },
    datePublished: "2024-01-01",
    dateModified: new Date().toISOString(),
    inLanguage: "en-US",
    isAccessibleForFree: true,
    isFamilyFriendly: true,
  };
}

export function generateBreadcrumbStructuredData() {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      {
        "@type": "ListItem",
        position: 1,
        name: "Home",
        item: siteConfig.url,
      },
    ],
  };
}

export function generateFAQStructuredData() {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: [
      {
        "@type": "Question",
        name: "What is codepot?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "codepot is a semantic metadata inference engine and template compiler that allows you to define facts once and generate infinite architecture outputs.",
        },
      },
      {
        "@type": "Question",
        name: "What programming languages does codepot support?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "codepot is built with TypeScript and can generate code for any language through codepot templates. It supports JavaScript, TypeScript, Python, Java, C#, and more.",
        },
      },
      {
        "@type": "Question",
        name: "Is codepot open source?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "Yes, codepot is open source under the MIT license. You can contribute to the project on GitHub.",
        },
      },
      {
        "@type": "Question",
        name: "What can I generate with codepot?",
        acceptedAnswer: {
          "@type": "Answer",
          text: "You can generate ORM entities, repositories, DTOs, validation layers, query builders, GraphQL schemas, OpenAPI specs, Zod schemas, React forms, admin panels, SDKs, and more.",
        },
      },
    ],
  };
}
