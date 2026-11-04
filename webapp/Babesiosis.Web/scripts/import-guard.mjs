#!/usr/bin/env node
// import-guard — zero-tolerance guard against relative TS import/export specifiers in
// Babesiosis.Web. Every file under src/app is reachable via a tsconfig.json path alias
// (the catch-all `app/*`, or a more specific one such as `@core/*` / `@reports/*` /
// `@layouts/*`) — so a relative specifier ('./x' or '../x') is never necessary and is
// always a guard failure, not a ratcheted baseline violation like fs-guard's.
//
// The fs-* shared components are not under src/: they come from the @fundstream-ai/gnome-ui
// package and are imported by package name.
//
// Modes:
//   node scripts/import-guard.mjs <path> [<path> ...]   single-file (Claude hook / pre-commit)
//   node scripts/import-guard.mjs --all                 full sweep (npm run lint / CI)
//
// Exit 0 = clean. Exit 2 = relative import(s) found — chosen so a PostToolUse hook feeds
// this script's stderr back to Claude for self-correction, same convention as fs-guard.mjs.

import { readFileSync, existsSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, relative, join, sep } from 'node:path';
import ts from 'typescript';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = resolve(SCRIPT_DIR, '..');
const APP_DIR = join(WEB_ROOT, 'src', 'app');

function relKey(absPath) {
  return relative(WEB_ROOT, absPath).split(sep).join('/');
}

function inScope(rel) {
  return rel.startsWith('src/app/') && rel.endsWith('.ts') && !rel.endsWith('.d.ts');
}

// Returns [{ line, specifier }] for every relative import/export/dynamic-import in the file.
function scanTs(absPath, text) {
  const source = ts.createSourceFile(absPath, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TS);
  const violations = [];

  function record(node) {
    if (!node || !ts.isStringLiteralLike(node)) return;
    if (!node.text.startsWith('.')) return;
    const { line } = source.getLineAndCharacterOfPosition(node.getStart(source));
    violations.push({ line: line + 1, specifier: node.text });
  }

  function visit(node) {
    if ((ts.isImportDeclaration(node) || ts.isExportDeclaration(node)) && node.moduleSpecifier) {
      record(node.moduleSpecifier);
    } else if (ts.isCallExpression(node) && node.expression.kind === ts.SyntaxKind.ImportKeyword && node.arguments.length) {
      record(node.arguments[0]);
    } else if (ts.isCallExpression(node) && ts.isIdentifier(node.expression) && node.expression.text === 'require' && node.arguments.length) {
      record(node.arguments[0]);
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  return violations.sort((a, b) => a.line - b.line);
}

function scanFile(absPath) {
  const rel = relKey(absPath);
  if (!inScope(rel)) return null;
  if (!existsSync(absPath)) return null;
  const violations = scanTs(absPath, readFileSync(absPath, 'utf8'));
  return violations.length ? { rel, violations } : null;
}

function walk(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else if (entry.isFile() && entry.name.endsWith('.ts') && !entry.name.endsWith('.d.ts')) out.push(full);
  }
  return out;
}

function report(blocking) {
  const lines = [];
  lines.push('import-guard: relative TS import found — use the tsconfig.json path alias instead\n');
  for (const { rel, violations } of blocking) {
    lines.push(rel);
    for (const v of violations) lines.push(`  L${v.line}  '${v.specifier}'`);
    lines.push('');
  }
  lines.push('Every file under src/app resolves via a path alias (app/*, or a more specific one');
  lines.push('such as @core/*, @reports/*, @layouts/*, @auth/*, @settings/*, @users/*, @roles/*,');
  lines.push('@employees/*, @component/* — see tsconfig.json "paths"). Rewrite the specifier to');
  lines.push('the alias form. See Babesiosis.Web/rules/absolute-imports.md.');
  return lines.join('\n');
}

function runFiles(paths) {
  const blocking = [];
  for (const p of paths) {
    const scanned = scanFile(resolve(process.cwd(), p));
    if (scanned) blocking.push(scanned);
  }
  if (blocking.length) {
    process.stderr.write(report(blocking) + '\n');
    process.exit(2);
  }
  process.exit(0);
}

function runAll() {
  const files = walk(APP_DIR).map(relKey).filter(inScope).sort();
  const blocking = [];
  for (const rel of files) {
    const scanned = scanFile(join(WEB_ROOT, rel));
    if (scanned) blocking.push(scanned);
  }
  if (blocking.length) {
    process.stderr.write(report(blocking) + '\n');
    process.exit(2);
  }
  process.stdout.write(`import-guard: clean — no relative TS imports in ${files.length} file(s).\n`);
  process.exit(0);
}

const args = process.argv.slice(2);
if (args.includes('--all')) {
  runAll();
} else if (args.length) {
  runFiles(args);
} else {
  process.stderr.write('usage: import-guard.mjs <path...> | --all\n');
  process.exit(1);
}
