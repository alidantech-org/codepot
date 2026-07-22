# CodePurify Project Structure

This document outlines the current structure of the CodePurify project after the reorganization into a package-based layout.

## Root Directory Structure

```
codepurify/
├── .github/                 # GitHub workflows and configuration
├── .gitignore              # Git ignore rules
├── LICENSE                 # Project license
├── README.md               # Main project documentation
├── docker-compose.yml      # Docker Compose configuration
├── docs/                   # Documentation files
├── extensions/             # IDE extensions
├── packages/               # Core packages for different platforms
├── site/                   # Documentation website
└── structure.md            # This file - project structure documentation
```

## Directory Details

### `packages/` - Core Packages
Contains the main CodePurify implementations for different platforms:

```
packages/
├── nodejs/                 # Node.js/TypeScript implementation
│   ├── src/               # Source code
│   ├── examples/          # Example configurations and templates
│   ├── package.json       # Node.js package configuration
│   └── ...                # Additional Node.js-specific files
└── python/                # Python implementation (placeholder)
    └── .gitkeep           # Placeholder for future Python package
```

### `extensions/` - IDE Extensions
Contains IDE-specific extensions and plugins:

```
extensions/
├── eclipse/               # Eclipse extension (placeholder)
│   └── .gitkeep           # Placeholder for future Eclipse extension
└── vscode/                # Visual Studio Code extension
    ├── src/               # Extension source code
    ├── examples/          # Example files for syntax highlighting
    ├── icons/             # Extension icons
    ├── syntaxes/          # Language syntax definitions
    ├── config/            # Language configuration files
    ├── package.json       # VSCode extension manifest
    └── ...                # Additional VSCode-specific files
```

### `site/` - Documentation Website
Next.js-based documentation and marketing website:

```
site/
├── src/                   # Next.js source code
│   ├── app/              # App router pages and API routes
│   ├── components/       # React components
│   ├── data/             # Site data and content
│   └── lib/              # Utility libraries
├── public/               # Static assets
├── Dockerfile            # Docker configuration for deployment
├── package.json          # Node.js dependencies
├── pnpm-lock.yaml        # Lock file for pnpm
├── next.config.ts        # Next.js configuration
└── ...                   # Additional web development files
```

### `docs/` - Additional Documentation
Contains supplementary documentation and project files:

```
docs/
├── txt/                  # Text-based documentation
└── ...                   # Additional documentation files
```

## Key Changes from Previous Structure

The project has been restructured from a monolithic layout to a package-based architecture:

- **Old**: `package/`, `vscode/`, `www/` directories
- **New**: `packages/`, `extensions/`, `site/` directories

This new structure provides:
- Better separation of concerns
- Platform-specific packaging
- Easier maintenance and development
- Clearer organization of different components

## Development Workflow

1. **Core Development**: Work in `packages/nodejs/` for the main CodePurify functionality
2. **Extension Development**: Work in `extensions/vscode/` for VSCode-specific features
3. **Documentation**: Work in `site/` for the website and documentation
4. **Testing**: Use `docker-compose.yml` for local development and testing

## Package Management

- **Node.js Package**: Uses npm/pnpm for dependency management
- **VSCode Extension**: Uses npm for packaging and publishing
- **Website**: Uses pnpm for Next.js dependency management
- **Docker**: Multi-stage builds for optimal deployment
