#!/usr/bin/env node
// PostToolUse stdin adapter for fs-guard. Claude pipes the tool-input JSON on stdin;
// we pull tool_input.file_path, gate to feature .html/.scss, then delegate to fs-guard.mjs.
// Exit 2 (with the guard's stderr) is propagated so Claude self-corrects in the same turn.

import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const GUARD = join(SCRIPT_DIR, 'fs-guard.mjs');

function getFilePath(raw) {
  if (!raw.trim()) return null;
  try {
    const payload = JSON.parse(raw);
    return payload?.tool_input?.file_path ?? payload?.tool_input?.filePath ?? null;
  } catch {
    return null;
  }
}

let raw = '';
try {
  raw = readFileSync(0, 'utf8'); // fd 0 = stdin
} catch {
  raw = '';
}

const filePath = getFilePath(raw);
if (!filePath || !/\.(html|scss)$/i.test(filePath)) {
  process.exit(0);
}

const result = spawnSync(process.execPath, [GUARD, filePath], {
  stdio: ['ignore', 'inherit', 'inherit'],
});
process.exit(result.status ?? 0);
