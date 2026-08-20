/**
 * Thin adapter between the React frontend and the authoritative Python backend.
 *
 * The Python files in `public/python/` (acquisition_engine.py, web_interface.py,
 * practice_cli.py, practice_analyzer.py) are the source of truth for every
 * calculation, score, default, and narrative. They are executed unmodified by a
 * real CPython interpreter (Pyodide/WebAssembly) loaded in the browser, and this
 * module only:
 *
 *   1. boots the interpreter,
 *   2. copies the .py files into its filesystem,
 *   3. calls `web_interface.analyze_acquisition(<decoded JSON request>)`,
 *   4. hands the returned JSON back to the UI, untouched.
 *
 * No acquisition logic lives here or anywhere else in the TypeScript codebase.
 * Backend maintenance (e.g. via Codex) only requires editing the files in
 * `public/python/`; the frontend contract is the JSON request/response defined
 * by web_interface.analyze_acquisition.
 */

import type { AnalysisRequest, AnalysisResponse } from "./types";

const PYODIDE_VERSION = "0.28.3";
const PYODIDE_INDEX_URL = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

/** Backend modules copied verbatim into the interpreter's filesystem. */
export const BACKEND_MODULES = [
  "acquisition_engine.py",
  "practice_cli.py",
  "practice_analyzer.py",
  "web_interface.py",
] as const;

type PyCallable = ((payload: string) => string) & { destroy?: () => void };

interface PyodideInterface {
  runPython: (code: string) => unknown;
  FS: { mkdirTree: (path: string) => void; writeFile: (path: string, data: string) => void };
}

declare global {
  interface Window {
    loadPyodide?: (options: { indexURL: string }) => Promise<PyodideInterface>;
  }
}

let bootPromise: Promise<PyCallable> | null = null;

function loadPyodideScript(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (window.loadPyodide) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = `${PYODIDE_INDEX_URL}pyodide.js`;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Could not load the Python analysis runtime."));
    document.head.appendChild(script);
  });
}

async function boot(): Promise<PyCallable> {
  await loadPyodideScript();
  if (!window.loadPyodide) throw new Error("Python runtime unavailable.");

  const pyodide = await window.loadPyodide({ indexURL: PYODIDE_INDEX_URL });

  const sources = await Promise.all(
    BACKEND_MODULES.map(async (name) => {
      const response = await fetch(`/python/${name}`);
      if (!response.ok) throw new Error(`Missing backend module: ${name}`);
      return [name, await response.text()] as const;
    }),
  );

  pyodide.FS.mkdirTree("/backend");
  for (const [name, source] of sources) {
    pyodide.FS.writeFile(`/backend/${name}`, source);
  }

  return pyodide.runPython(`
import sys, json
if "/backend" not in sys.path:
    sys.path.insert(0, "/backend")
import web_interface

def _bridge(payload):
    return json.dumps(web_interface.analyze_acquisition(json.loads(payload)))

_bridge
`) as PyCallable;
}

/** Warm the interpreter ahead of time so submitting results feels immediate. */
export function preloadAnalysisRuntime(): void {
  if (typeof window === "undefined") return;
  if (!bootPromise) bootPromise = boot();
  void bootPromise.catch(() => {
    bootPromise = null;
  });
}

/**
 * Run one analysis through the existing Python web interface.
 * The returned object is exactly what `analyze_acquisition` produced.
 */
export async function analyzeAcquisition(request: AnalysisRequest): Promise<AnalysisResponse> {
  if (!bootPromise) bootPromise = boot();
  let bridge: PyCallable;
  try {
    bridge = await bootPromise;
  } catch (error) {
    bootPromise = null;
    throw error;
  }
  return JSON.parse(bridge(JSON.stringify(request))) as AnalysisResponse;
}
