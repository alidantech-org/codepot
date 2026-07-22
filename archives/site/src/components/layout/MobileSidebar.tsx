"use client";

import Link from "next/link";
import { X, Package, Code } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import { GitHubIcon } from "@/components/icons/GitHubIcon";

interface MobileSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileSidebar({ isOpen, onClose }: MobileSidebarProps) {
  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-60 bg-black/50 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-70 w-64 bg-card border-r border-border transform transition-transform duration-300 ease-in-out lg:hidden ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-full flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border">
            <Link
              href="/"
              className="flex items-center gap-2.5"
              onClick={onClose}
            >
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-linear-to-br from-primary to-secondary font-mono text-[11px] font-medium text-white">
                cp
              </span>
              <span className="text-xl font-bold tracking-tight bg-linear-to-r from-primary to-secondary bg-clip-text text-transparent">
                CodePurify
              </span>
            </Link>
            <button
              onClick={onClose}
              className="rounded-md p-2 text-muted-foreground hover:bg-card-muted hover:text-foreground"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 overflow-y-auto p-4">
            <div className="space-y-2">
              <Link
                href="#features"
                className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted"
                onClick={onClose}
              >
                Features
              </Link>
              <Link
                href="#pipeline"
                className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted"
                onClick={onClose}
              >
                Pipeline
              </Link>
              <Link
                href="#examples"
                className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted"
                onClick={onClose}
              >
                Examples
              </Link>
              <Link
                href="/docs"
                className="block rounded-md px-3 py-2 text-sm font-medium text-foreground hover:bg-card-muted"
                onClick={onClose}
              >
                Documentation
              </Link>
            </div>

            {/* External Links */}
            <div className="mt-8 space-y-2">
              <div className="px-3 py-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Links
              </div>
              <a
                href="https://github.com/alidantech-org/codepurify"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-foreground hover:bg-card-muted"
              >
                <GitHubIcon />
                GitHub
              </a>
              <a
                href="https://www.npmjs.com/package/codepurify"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-foreground hover:bg-card-muted"
              >
                <Package className="h-4 w-4" />
                NPM
              </a>
              <a
                href="https://marketplace.visualstudio.com/items?itemName=alidantechorg.codepurify-templates&ssr=false#overview"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-foreground hover:bg-card-muted"
              >
                <Code className="h-4 w-4" />
                VSCode
              </a>
            </div>
          </nav>

          {/* Footer */}
          <div className="border-t border-border p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">Theme</span>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
