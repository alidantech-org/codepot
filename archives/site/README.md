# Codepurify Documentation Website

This is the official documentation website for [Codepurify](https://github.com/alidantech-org/codepurify) - a semantic metadata inference engine and template compiler for generating architecture artifacts from typed domain configs.

## About Codepurify

Codepurify is a powerful tool that allows you to:

- Define semantic metadata in strongly-typed TypeScript configs
- Infer query capabilities, mutation semantics, and relation groups
- Generate architecture artifacts through Codepurify templates
- Create framework-agnostic code generation systems

## Getting Started

### Development

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the documentation website.

### Building for Production

```bash
npm run build
npm start
```

### Making Changes

You can start editing the documentation by modifying `app/page.tsx`. The page auto-updates as you edit the file.

## Technology Stack

- **[Next.js](https://nextjs.org)** - React framework for the documentation site
- **[Tailwind CSS](https://tailwindcss.com)** - Utility-first CSS framework
- **[TypeScript](https://typescriptlang.org)** - Type-safe development
- **[Geist](https://vercel.com/font)** - Modern font family optimized for Vercel

## Project Structure

```
www/
├── public/          # Static assets (logo, favicon)
├── src/
│   ├── app/         # Next.js app router pages
│   └── components/  # Reusable React components
├── package.json
└── README.md
```

## Contributing

This documentation website is part of the Codepurify project. To contribute:

1. Fork the [Codepurify repository](https://github.com/alidantech-org/codepurify)
2. Make changes to the documentation in the `www/` directory
3. Submit a pull request

## Learn More

- **[Codepurify Core Documentation](https://github.com/alidantech-org/codepurify#readme)** - Learn about the semantic metadata engine
- **[Next.js Documentation](https://nextjs.org/docs)** - Learn about Next.js features and API
- **[Tailwind CSS Documentation](https://tailwindcss.com/docs)** - Learn about utility-first CSS framework

## Deploy

The easiest way to deploy this documentation website is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
