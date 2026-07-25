import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  poweredByHeader: false,
  reactStrictMode: true,
  async redirects() {
    return [
      {
        source: "/docs/codepot-openapi",
        destination: "/docs/packages/codepot-openapi",
        permanent: true,
      },
      {
        source: "/docs/codepotg",
        destination: "/docs/packages/codepotg",
        permanent: true,
      },
      {
        source: "/docs/codepotx",
        destination: "/docs/packages/codepotx",
        permanent: true,
      },
      {
        source: "/docs/codepotx-cli",
        destination: "/docs/packages/codepotx-cli",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
