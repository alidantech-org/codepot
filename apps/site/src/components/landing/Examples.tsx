'use client';

import { javascript } from '@codemirror/lang-javascript';
import { yaml } from '@codemirror/lang-yaml';
import { oneDark } from '@codemirror/theme-one-dark';
import CodeMirror from '@uiw/react-codemirror';
import { Ellipsis, Maximize2, Minus, Plus, X } from 'lucide-react';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';

import type { WorkflowCodeExample, WorkflowExampleKey } from '@/data/types';

import styles from './Examples.module.css';

interface ExamplesProps {
  examples: WorkflowCodeExample[];
}

const EDITOR_SCALES = [0.86, 1, 1.14] as const;
const EDITOR_HEIGHTS = ['22rem', '28rem', '35rem'] as const;

function languageExtension(language: string) {
  if (language === 'yaml' || language === 'yml') return yaml();

  return javascript({
    typescript: language === 'typescript' || language === 'tsx' || language === 'jinja',
    jsx: language === 'jsx' || language === 'tsx'
  });
}

function createDrafts(examples: WorkflowCodeExample[]): Record<WorkflowExampleKey, string> {
  return Object.fromEntries(examples.map((example) => [example.key, example.code])) as Record<
    WorkflowExampleKey,
    string
  >;
}

export function Examples({ examples }: ExamplesProps) {
  const { resolvedTheme } = useTheme();
  const examplesByKey = useMemo(
    () =>
      Object.fromEntries(examples.map((example) => [example.key, example])) as Record<
        WorkflowExampleKey,
        WorkflowCodeExample
      >,
    [examples]
  );
  const allKeys = useMemo(() => examples.map((example) => example.key), [examples]);
  const [activeKey, setActiveKey] = useState<WorkflowExampleKey>(examples[0]?.key ?? 'contract');
  const [openKeys, setOpenKeys] = useState<WorkflowExampleKey[]>(() => [...allKeys]);
  const [drafts, setDrafts] = useState<Record<WorkflowExampleKey, string>>(() => createDrafts(examples));
  const [menuOpen, setMenuOpen] = useState(false);
  const [fontSize, setFontSize] = useState(11);
  const [scaleIndex, setScaleIndex] = useState(0);
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);

  const activeExample = openKeys.includes(activeKey) ? examplesByKey[activeKey] : undefined;
  const extensions = useMemo(() => (activeExample ? [languageExtension(activeExample.language)] : []), [activeExample]);
  const editorScale = EDITOR_SCALES[scaleIndex];

  useEffect(() => {
    if (!isFullscreen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setIsFullscreen(false);
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isFullscreen]);

  function openFile(key: WorkflowExampleKey) {
    setOpenKeys((current) => (current.includes(key) ? current : [...current, key]));
    setActiveKey(key);
  }

  function closeFile(key: WorkflowExampleKey) {
    setOpenKeys((current) => {
      const index = current.indexOf(key);
      const next = current.filter((candidate) => candidate !== key);

      if (key === activeKey) {
        const nextActive = next[index] ?? next[index - 1] ?? next[0];
        if (nextActive) setActiveKey(nextActive);
      }

      return next;
    });
  }

  function reopenAllFiles() {
    setOpenKeys([...allKeys]);
    setActiveKey(allKeys[0] ?? activeKey);
    setMenuOpen(false);
  }

  function closeAllFiles() {
    setOpenKeys([]);
    setMenuOpen(false);
  }

  function changeFontSize(delta: number) {
    setFontSize((current) => Math.min(18, Math.max(9, current + delta)));
  }

  function changeScale(delta: number) {
    setScaleIndex((current) => Math.min(EDITOR_SCALES.length - 1, Math.max(0, current + delta)));
  }

  function renderWorkspace(fullscreen: boolean) {
    const workspaceStyle = {
      '--editor-font-size': `${fontSize}px`,
      '--editor-scale': editorScale
    } as CSSProperties;

    return (
      <div
        className={`${styles.workspace} ${fullscreen ? styles.fullscreenWorkspace : ''}`}
        style={workspaceStyle}
      >
        <div className={styles.editorBar}>
          <div className={styles.tabBar} role="tablist" aria-label="Open workflow files">
            {openKeys.map((key) => {
              const example = examplesByKey[key];
              if (!example) return null;

              const isActive = key === activeKey;
              return (
                <div
                  key={key}
                  className={`${styles.tab} ${isActive ? styles.activeTab : ''}`}
                  role="tab"
                  aria-selected={isActive}
                >
                  <button
                    type="button"
                    onClick={() => setActiveKey(key)}
                    className={styles.tabLabel}
                    title={example.filename}
                  >
                    {example.filename}
                  </button>
                  <button
                    type="button"
                    onClick={() => closeFile(key)}
                    className={styles.closeButton}
                    aria-label={`Close ${example.filename}`}
                  >
                    <X aria-hidden="true" />
                  </button>
                </div>
              );
            })}
          </div>

          <div className={styles.editorActions}>
            {fullscreen && (
              <button
                type="button"
                className={styles.actionButton}
                onClick={() => setIsFullscreen(false)}
                aria-label="Exit full screen"
              >
                <X aria-hidden="true" />
              </button>
            )}
            <button
              type="button"
              className={styles.moreButton}
              onClick={() => setMenuOpen((current) => !current)}
              aria-label="More editor options"
              aria-expanded={menuOpen}
            >
              <Ellipsis aria-hidden="true" />
            </button>
          </div>

          {menuOpen && (
            <div className={styles.menu} role="menu">
              <div className={styles.menuGroup}>
                <span className={styles.menuLabel}>Font size</span>
                <div className={styles.stepper}>
                  <button type="button" onClick={() => changeFontSize(-1)} aria-label="Decrease font size">
                    <Minus aria-hidden="true" />
                  </button>
                  <span>{fontSize}px</span>
                  <button type="button" onClick={() => changeFontSize(1)} aria-label="Increase font size">
                    <Plus aria-hidden="true" />
                  </button>
                </div>
              </div>

              <div className={styles.menuGroup}>
                <span className={styles.menuLabel}>Editor scale</span>
                <div className={styles.stepper}>
                  <button type="button" onClick={() => changeScale(-1)} aria-label="Decrease editor scale">
                    <Minus aria-hidden="true" />
                  </button>
                  <span>{Math.round(editorScale * 100)}%</span>
                  <button type="button" onClick={() => changeScale(1)} aria-label="Increase editor scale">
                    <Plus aria-hidden="true" />
                  </button>
                </div>
              </div>

              <button
                type="button"
                className={styles.menuButton}
                onClick={() => setShowLineNumbers((current) => !current)}
                role="menuitemcheckbox"
                aria-checked={showLineNumbers}
              >
                <span>Line numbers</span>
                <span>{showLineNumbers ? 'On' : 'Off'}</span>
              </button>
              <button type="button" className={styles.menuButton} onClick={reopenAllFiles} role="menuitem">
                Open all files
              </button>
              <button type="button" className={styles.menuButton} onClick={closeAllFiles} role="menuitem">
                Close all files
              </button>
              {!fullscreen && (
                <button
                  type="button"
                  className={styles.menuButton}
                  onClick={() => {
                    setIsFullscreen(true);
                    setMenuOpen(false);
                  }}
                  role="menuitem"
                >
                  <span>Open full screen</span>
                  <Maximize2 aria-hidden="true" />
                </button>
              )}
            </div>
          )}
        </div>

        {activeExample ? (
          <CodeMirror
            value={drafts[activeKey] ?? activeExample.code}
            onChange={(value) =>
              setDrafts((current) => ({
                ...current,
                [activeKey]: value
              }))
            }
            extensions={extensions}
            theme={resolvedTheme === 'dark' ? oneDark : 'light'}
            height={fullscreen ? 'calc(100dvh - 2.15rem)' : EDITOR_HEIGHTS[scaleIndex]}
            width="100%"
            basicSetup={{
              lineNumbers: showLineNumbers,
              foldGutter: showLineNumbers,
              highlightActiveLine: true,
              highlightActiveLineGutter: showLineNumbers,
              bracketMatching: true,
              closeBrackets: true,
              autocompletion: true,
              indentOnInput: true,
              syntaxHighlighting: true
            }}
            aria-label={`Editable ${activeExample.filename} example`}
            className={styles.editor}
          />
        ) : (
          <div className={styles.emptyState} style={{ minHeight: fullscreen ? 'calc(100dvh - 2.15rem)' : EDITOR_HEIGHTS[scaleIndex] }}>
            <button type="button" onClick={reopenAllFiles} className="text-primary hover:underline">
              Open a workflow file
            </button>
          </div>
        )}
      </div>
    );
  }

  return (
    <section id="examples" className="border-y border-border bg-card/35">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">Workflows</p>
        <h2 className="max-w-4xl text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">
          Real files from contract to generated code
        </h2>
        <p className="mt-4 max-w-3xl text-[15px] leading-7 text-muted-foreground">
          Each tab is loaded from a real source file in the website project. Edit the contract, CodepotG task, paths
          configuration, or Jinja template in the shared syntax-highlighted editor.
        </p>

        <div className="mt-8 grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(18rem,24rem)] xl:items-stretch">
          <div className="order-2 xl:order-1">{renderWorkspace(false)}</div>

          <div className="order-1 grid gap-2 sm:grid-cols-2 xl:order-2 xl:grid-cols-1 xl:content-start">
            {examples.map((example) => {
              const isActive = activeKey === example.key && openKeys.includes(example.key);
              return (
                <button
                  key={example.key}
                  type="button"
                  onClick={() => openFile(example.key)}
                  aria-pressed={isActive}
                  className={`group min-w-0 border-l-2 px-4 py-4 text-left transition-colors sm:border-l-0 sm:border-t-2 xl:border-l-2 xl:border-t-0 ${
                    isActive
                      ? 'border-primary bg-primary/8'
                      : 'border-border hover:border-primary/45 hover:bg-card-muted/45'
                  }`}
                >
                  <span className="font-mono text-[10px] uppercase tracking-widest text-primary">
                    {example.eyebrow}
                  </span>
                  <span className="mt-2 block text-sm font-semibold text-foreground">{example.title}</span>
                  <span className="mt-2 block text-sm leading-6 text-muted-foreground">{example.description}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-6 text-sm text-muted-foreground">
          <Link href="/docs/prototype-workflow" className="font-medium text-primary hover:underline">
            Read the complete prototype workflow
          </Link>
          <span className="mx-2">·</span>
          <Link href="/docs/template-packs" className="font-medium text-foreground hover:underline">
            Learn about template packs
          </Link>
        </div>
      </div>

      {isFullscreen && (
        <div className={styles.fullscreenOverlay} role="dialog" aria-modal="true" aria-label="Workflow code editor">
          {renderWorkspace(true)}
        </div>
      )}
    </section>
  );
}
