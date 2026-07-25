'use client';

import { javascript } from '@codemirror/lang-javascript';
import { yaml } from '@codemirror/lang-yaml';
import { oneDark } from '@codemirror/theme-one-dark';
import CodeMirror from '@uiw/react-codemirror';
import {
  ChevronDown,
  Ellipsis,
  FileCode2,
  FilePlus2,
  FolderOpen,
  Maximize2,
  Minus,
  Plus,
  Trash2,
  X
} from 'lucide-react';
import Link from 'next/link';
import { useTheme } from 'next-themes';
import { useEffect, useMemo, useState } from 'react';
import { createPortal } from 'react-dom';
import type { CSSProperties } from 'react';

import type { WorkflowCodeExample } from '@/data/types';

import styles from './Examples.module.css';

interface ExamplesProps {
  examples: WorkflowCodeExample[];
}

interface EditorFile {
  id: string;
  filename: string;
  language: string;
  code: string;
}

const EDITOR_SCALES = [0.86, 1, 1.14] as const;
const DEFAULT_EDITOR_HEIGHT = 'clamp(25.5rem, 49.3vw, 37.4rem)';

function languageExtension(language: string) {
  if (language === 'yaml' || language === 'yml') return yaml();

  return javascript({
    typescript: language === 'typescript' || language === 'tsx' || language === 'jinja',
    jsx: language === 'jsx' || language === 'tsx'
  });
}

function inferLanguage(filename: string) {
  const extension = filename.split('.').pop()?.toLowerCase();
  if (extension === 'yaml' || extension === 'yml') return 'yaml';
  if (extension === 'tsx') return 'tsx';
  if (extension === 'jsx') return 'jsx';
  if (extension === 'j2' || extension === 'jinja') return 'jinja';
  return 'typescript';
}

function initialFiles(examples: WorkflowCodeExample[]): EditorFile[] {
  return examples.map((example) => ({
    id: example.key,
    filename: example.filename,
    language: example.language,
    code: example.code
  }));
}

export function Examples({ examples }: ExamplesProps) {
  const { resolvedTheme } = useTheme();
  const originalExamples = useMemo(
    () => new Map(examples.map((example) => [example.key, example])),
    [examples]
  );
  const [files, setFiles] = useState<EditorFile[]>(() => initialFiles(examples));
  const [activeId, setActiveId] = useState<string>(examples[0]?.key ?? 'contract');
  const [openIds, setOpenIds] = useState<string[]>(() => examples.map((example) => example.key));
  const [menuOpen, setMenuOpen] = useState(false);
  const [fontSize, setFontSize] = useState(11);
  const [scaleIndex, setScaleIndex] = useState(0);
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [isCreatingFile, setIsCreatingFile] = useState(false);
  const [explorerOpen, setExplorerOpen] = useState(true);

  const filesById = useMemo(() => new Map(files.map((file) => [file.id, file])), [files]);
  const activeFile = openIds.includes(activeId) ? filesById.get(activeId) : undefined;
  const extensions = useMemo(() => (activeFile ? [languageExtension(activeFile.language)] : []), [activeFile]);
  const editorScale = EDITOR_SCALES[scaleIndex];
  const lineCount = activeFile ? activeFile.code.split('\n').length : 0;

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

  function ensureFile(id: string) {
    const existing = filesById.get(id);
    if (existing) return existing;

    const original = originalExamples.get(id as WorkflowCodeExample['key']);
    if (!original) return undefined;

    const restored: EditorFile = {
      id: original.key,
      filename: original.filename,
      language: original.language,
      code: original.code
    };
    setFiles((current) => [...current, restored]);
    return restored;
  }

  function openFile(id: string) {
    const file = ensureFile(id);
    if (!file) return;
    setOpenIds((current) => (current.includes(id) ? current : [...current, id]));
    setActiveId(id);
  }

  function closeFile(id: string) {
    setOpenIds((current) => {
      const index = current.indexOf(id);
      const next = current.filter((candidate) => candidate !== id);
      if (id === activeId) {
        const nextActive = next[index] ?? next[index - 1] ?? next[0];
        if (nextActive) setActiveId(nextActive);
      }
      return next;
    });
  }

  function deleteFile(id: string) {
    setFiles((current) => current.filter((file) => file.id !== id));
    closeFile(id);
  }

  function createFile() {
    const filename = newFileName.trim();
    if (!filename) return;

    const id = `custom-${Date.now()}`;
    const file: EditorFile = {
      id,
      filename,
      language: inferLanguage(filename),
      code: ''
    };
    setFiles((current) => [...current, file]);
    setOpenIds((current) => [...current, id]);
    setActiveId(id);
    setNewFileName('');
    setIsCreatingFile(false);
  }

  function reopenAllFiles() {
    const restored = initialFiles(examples);
    setFiles((current) => {
      const existingIds = new Set(current.map((file) => file.id));
      return [...current, ...restored.filter((file) => !existingIds.has(file.id))];
    });
    setOpenIds((current) => Array.from(new Set([...current, ...restored.map((file) => file.id)])));
    setActiveId(restored[0]?.id ?? activeId);
    setMenuOpen(false);
  }

  function closeAllFiles() {
    setOpenIds([]);
    setMenuOpen(false);
  }

  function changeFontSize(delta: number) {
    setFontSize((current) => Math.min(18, Math.max(9, current + delta)));
  }

  function changeScale(delta: number) {
    setScaleIndex((current) => Math.min(EDITOR_SCALES.length - 1, Math.max(0, current + delta)));
  }

  function updateActiveFile(code: string) {
    setFiles((current) => current.map((file) => (file.id === activeId ? { ...file, code } : file)));
  }

  function renderEditorPane(fullscreen: boolean) {
    const workspaceStyle = {
      '--editor-font-size': `${fontSize}px`,
      '--editor-scale': editorScale
    } as CSSProperties;

    return (
      <div className={styles.editorPane} style={workspaceStyle}>
        <div className={styles.editorBar}>
          <div className={styles.tabBar} role="tablist" aria-label="Open workflow files">
            {openIds.map((id) => {
              const file = filesById.get(id);
              if (!file) return null;
              const isActive = id === activeId;
              return (
                <div key={id} className={`${styles.tab} ${isActive ? styles.activeTab : ''}`} role="tab" aria-selected={isActive}>
                  <button type="button" onClick={() => setActiveId(id)} className={styles.tabLabel} title={file.filename}>
                    {file.filename}
                  </button>
                  <button type="button" onClick={() => closeFile(id)} className={styles.closeButton} aria-label={`Close ${file.filename}`}>
                    <X aria-hidden="true" />
                  </button>
                </div>
              );
            })}
          </div>

          <div className={styles.editorActions}>
            {fullscreen && (
              <button type="button" className={styles.actionButton} onClick={() => setIsFullscreen(false)} aria-label="Exit full screen">
                <X aria-hidden="true" />
              </button>
            )}
            <button type="button" className={styles.moreButton} onClick={() => setMenuOpen((current) => !current)} aria-label="More editor options" aria-expanded={menuOpen}>
              <Ellipsis aria-hidden="true" />
            </button>
          </div>

          {menuOpen && (
            <div className={styles.menu} role="menu">
              <div className={styles.menuGroup}>
                <span className={styles.menuLabel}>Font size</span>
                <div className={styles.stepper}>
                  <button type="button" onClick={() => changeFontSize(-1)} aria-label="Decrease font size"><Minus aria-hidden="true" /></button>
                  <span>{fontSize}px</span>
                  <button type="button" onClick={() => changeFontSize(1)} aria-label="Increase font size"><Plus aria-hidden="true" /></button>
                </div>
              </div>
              <div className={styles.menuGroup}>
                <span className={styles.menuLabel}>Editor scale</span>
                <div className={styles.stepper}>
                  <button type="button" onClick={() => changeScale(-1)} aria-label="Decrease editor scale"><Minus aria-hidden="true" /></button>
                  <span>{Math.round(editorScale * 100)}%</span>
                  <button type="button" onClick={() => changeScale(1)} aria-label="Increase editor scale"><Plus aria-hidden="true" /></button>
                </div>
              </div>
              <button type="button" className={styles.menuButton} onClick={() => setShowLineNumbers((current) => !current)} role="menuitemcheckbox" aria-checked={showLineNumbers}>
                <span>Line numbers</span><span>{showLineNumbers ? 'On' : 'Off'}</span>
              </button>
              <button type="button" className={styles.menuButton} onClick={reopenAllFiles} role="menuitem">Open all files</button>
              <button type="button" className={styles.menuButton} onClick={closeAllFiles} role="menuitem">Close all files</button>
              {!fullscreen && (
                <button type="button" className={styles.menuButton} onClick={() => { setIsFullscreen(true); setMenuOpen(false); }} role="menuitem">
                  <span>Open full screen</span><Maximize2 aria-hidden="true" />
                </button>
              )}
            </div>
          )}
        </div>

        {activeFile ? (
          <CodeMirror
            value={activeFile.code}
            onChange={updateActiveFile}
            extensions={extensions}
            theme={resolvedTheme === 'dark' ? oneDark : 'light'}
            height={fullscreen ? 'calc(100dvh - 4.2rem)' : DEFAULT_EDITOR_HEIGHT}
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
            aria-label={`Editable ${activeFile.filename} example`}
            className={styles.editor}
          />
        ) : (
          <div className={styles.emptyState} style={{ minHeight: fullscreen ? 'calc(100dvh - 4.2rem)' : DEFAULT_EDITOR_HEIGHT }}>
            <button type="button" onClick={reopenAllFiles} className="text-primary hover:underline">Open a workflow file</button>
          </div>
        )}

        {fullscreen && (
          <div className={styles.statusBar}>
            <span>main*</span>
            <span>{activeFile?.language ?? 'Plain Text'}</span>
            <span>{lineCount} lines</span>
            <span>Spaces: 2</span>
            <span>UTF-8</span>
          </div>
        )}
      </div>
    );
  }

  function renderFullscreenWorkspace() {
    return (
      <div className={styles.fullscreenOverlay} role="dialog" aria-modal="true" aria-label="Workflow code editor">
        <div className={styles.fullscreenWorkspace}>
          <aside className={styles.explorer} aria-label="File explorer">
            <div className={styles.explorerHeader}>
              <span>EXPLORER</span>
              <button type="button" onClick={() => setIsCreatingFile(true)} aria-label="Create file"><FilePlus2 aria-hidden="true" /></button>
            </div>
            <button type="button" className={styles.folderRow} onClick={() => setExplorerOpen((current) => !current)}>
              <ChevronDown className={explorerOpen ? '' : styles.collapsedChevron} aria-hidden="true" />
              <FolderOpen aria-hidden="true" />
              <span>workflow</span>
            </button>
            {explorerOpen && (
              <div className={styles.fileTree}>
                {files.map((file) => (
                  <div key={file.id} className={`${styles.fileRow} ${file.id === activeId ? styles.activeFileRow : ''}`}>
                    <button type="button" onClick={() => openFile(file.id)} title={file.filename}>
                      <FileCode2 aria-hidden="true" />
                      <span>{file.filename}</span>
                    </button>
                    <button type="button" onClick={() => deleteFile(file.id)} aria-label={`Delete ${file.filename}`} className={styles.deleteFileButton}>
                      <Trash2 aria-hidden="true" />
                    </button>
                  </div>
                ))}
                {isCreatingFile && (
                  <form className={styles.newFileForm} onSubmit={(event) => { event.preventDefault(); createFile(); }}>
                    <FileCode2 aria-hidden="true" />
                    <input autoFocus value={newFileName} onChange={(event) => setNewFileName(event.target.value)} onBlur={() => { if (!newFileName.trim()) setIsCreatingFile(false); }} placeholder="filename.ts" aria-label="New file name" />
                  </form>
                )}
              </div>
            )}
          </aside>
          {renderEditorPane(true)}
        </div>
      </div>
    );
  }

  return (
    <section id="examples" className="border-y border-border bg-card/35">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 sm:py-16 lg:px-8 lg:py-20">
        <p className="mb-3 font-mono text-[11px] uppercase tracking-widest text-accent">Workflows</p>
        <h2 className="max-w-4xl text-3xl font-semibold tracking-tight text-foreground sm:text-4xl">Real files from contract to generated code</h2>
        <p className="mt-4 max-w-3xl text-[15px] leading-7 text-muted-foreground">Each tab is loaded from a real source file in the website project. Edit the contract, CodepotG task, paths configuration, or Jinja template in the shared syntax-highlighted editor.</p>

        <div className="mt-8 grid min-w-0 gap-6 xl:grid-cols-[minmax(0,1fr)_minmax(18rem,24rem)] xl:items-stretch">
          <div className={`${styles.workspace} order-2 xl:order-1`}>{renderEditorPane(false)}</div>
          <div className="order-1 grid gap-2 sm:grid-cols-2 xl:order-2 xl:grid-cols-1 xl:content-start">
            {examples.map((example) => {
              const isActive = activeId === example.key && openIds.includes(example.key);
              return (
                <button key={example.key} type="button" onClick={() => openFile(example.key)} aria-pressed={isActive} className={`group min-w-0 border-l-2 px-4 py-4 text-left transition-colors sm:border-l-0 sm:border-t-2 xl:border-l-2 xl:border-t-0 ${isActive ? 'border-primary bg-primary/8' : 'border-border hover:border-primary/45 hover:bg-card-muted/45'}`}>
                  <span className="font-mono text-[10px] uppercase tracking-widest text-primary">{example.eyebrow}</span>
                  <span className="mt-2 block text-sm font-semibold text-foreground">{example.title}</span>
                  <span className="mt-2 block text-sm leading-6 text-muted-foreground">{example.description}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-6 text-sm text-muted-foreground">
          <Link href="/docs/prototype-workflow" className="font-medium text-primary hover:underline">Read the complete prototype workflow</Link>
          <span className="mx-2">·</span>
          <Link href="/docs/template-packs" className="font-medium text-foreground hover:underline">Learn about template packs</Link>
        </div>
      </div>

      {isFullscreen && typeof document !== 'undefined' ? createPortal(renderFullscreenWorkspace(), document.body) : null}
    </section>
  );
}
