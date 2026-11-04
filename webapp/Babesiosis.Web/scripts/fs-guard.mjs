#!/usr/bin/env node
// fs-guard — deterministic shared-component-library discipline guard for Babesiosis.Web.
//
// Enforces (in FEATURE templates):
//   R1 raw <button>           -> <fs-button>
//   R2 raw <input>            -> <fs-text-input> / fs-checkbox / fs-radio / fs-date-picker / fs-time-picker
//   R3 raw <select>           -> <fs-select> / <fs-multi-select>
//   R4 raw <textarea>         -> <fs-textarea>
//   R5 raw <table>            -> <fs-data-table>
//   R6 raw icon (<svg>, <i class>, <iconify-icon>, <mat-icon>) -> <fs-symbol>
//   R7 <mat-*> element        -> the fs-* equivalent
//   R8 <dx-*> element         -> <fs-data-table> (DevExtreme removed; never reintroduce)
//   R9 literal colour in a style attr/binding or .scss -> a var(--fs-*) / var(--bs-*) token
//   R10 provenance string (vuexy/larkon/pixinvent/devexpress/devextreme) in .html/.scss
//   R11 banned grid library in package.json -> the only sanctioned grid engine is TanStack
//       (@tanstack/*), used headless inside <fs-data-table>. Any other grid lib (devextreme,
//       ag-grid, kendo, syncfusion, handsontable, tabulator, …) fails the build.
//
// The fs-* components themselves live in the @fundstream-ai/gnome-ui package (repository
// fundstream-ai/gnome-ui), which has its own lint; nothing under src/ is library code.
//
// PREVENTION-FIRST RATCHET: a checked-in baseline (.fs-guard-baseline.json) grandfathers
// the violations that exist today. The guard blocks only NEW violations — a per-(file,rule)
// count that exceeds the baseline, or any violation in a file/rule not in the baseline.
// Remediation lowers counts; re-run --update-baseline to lock the improvement in.
//
// Modes:
//   node scripts/fs-guard.mjs <path> [<path> ...]   single-file (Claude hook / pre-commit)
//   node scripts/fs-guard.mjs --all                 full sweep + Mechanism B (npm run lint / CI)
//   node scripts/fs-guard.mjs --update-baseline     re-snapshot the baseline from current state
//
// Exit 0 = clean (no NEW violations). Exit 2 = new violation(s) — chosen so a PostToolUse
// hook feeds this script's stderr back to Claude for self-correction.

import { readFileSync, writeFileSync, existsSync, readdirSync, statSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve, relative, join, sep } from 'node:path';

const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));
const WEB_ROOT = resolve(SCRIPT_DIR, '..');                 // Babesiosis.Web
const APP_DIR = join(WEB_ROOT, 'src', 'app');
const BASELINE_PATH = join(WEB_ROOT, '.fs-guard-baseline.json');
const PACKAGE_JSON = join(WEB_ROOT, 'package.json');

// R11 — banned grid libraries. The ONLY sanctioned grid engine is TanStack (@tanstack/*),
// used headless *inside* <fs-data-table> so the styling/filters/pills stay ours. Any other
// grid library in package.json is blocked — re-adding DevExtreme or pulling in AG Grid /
// Kendo / Syncfusion / Handsontable / etc. fails the build regardless of who's editing.
// Intentionally version-agnostic: matches package names, never versions. @tanstack/* is allowed.
const BANNED_GRID_DEPS = [
  /^devextreme(-angular|-aspnet-data)?$/i,
  /^ag-grid(-community|-angular|-enterprise|-charts.*)?$/i,
  /^@ag-grid-(community|enterprise|charts)\//i,
  /^@progress\/kendo-angular-grid$/i,
  /^@syncfusion\/ej2-(angular-)?grids$/i,
  /^handsontable$/i,
  /^@handsontable\/angular(-wrapper)?$/i,
  /^tabulator-tables$/i,
  /^ngx-datatable$/i,
  /^@swimlane\/ngx-datatable$/i,
  /^@revolist\/(revogrid|angular-datagrid)$/i,
  /^@glideapps\/glide-data-grid$/i,
  /^slickgrid(-react|-vue|-universal)?$/i,
  /^@bryntum\/grid(-angular)?$/i,
  /^@mui\/x-data-grid.*$/i,
];

function checkBannedGridDeps() {
  if (!existsSync(PACKAGE_JSON)) return [];
  let pkg;
  try {
    pkg = JSON.parse(readFileSync(PACKAGE_JSON, 'utf8'));
  } catch {
    return [];
  }
  const found = [];
  for (const section of ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies']) {
    const deps = pkg[section];
    if (!deps) continue;
    for (const name of Object.keys(deps)) {
      if (BANNED_GRID_DEPS.some(re => re.test(name))) found.push({ name, section });
    }
  }
  return found;
}

// Paths the guard never scans: the shell chrome is out of feature scope.
// This is a shrinking ratchet — entries leave as migration completes, never grow to hide debt.
const EXEMPT_PREFIXES = [
  'src/app/layout/',
];

const RULE_FIX = {
  R1: 'raw <button> — use <fs-button>',
  R2: 'raw <input> — use <fs-text-input> (or <fs-checkbox>/<fs-radio>/<fs-date-picker>/<fs-time-picker> by type)',
  R3: 'raw <select> — use <fs-select> / <fs-multi-select>',
  R4: 'raw <textarea> — use <fs-textarea>',
  R5: 'raw <table> — every grid uses <fs-data-table>',
  R6: 'raw icon — use <fs-symbol>',
  R7: 'raw <mat-*> element — use the fs-* equivalent',
  R8: 'raw <dx-*> element — use <fs-data-table> (DevExtreme is removed; never reintroduce)',
  R9: 'literal colour — use a var(--fs-*) / var(--bs-*) token',
  R10: 'provenance string — remove the source-template reference',
  R11: 'the only sanctioned grid engine is TanStack (@tanstack/*), used headless inside <fs-data-table>',
};

const PROVENANCE_RE = /\b(vuexy|larkon|pixinvent|devexpress|devextreme)\b/gi;
// A *literal* colour: a hex value, or rgb()/hsl() whose first argument is a numeric
// literal. Crucially this does NOT match the project's standard token composition
// `rgb(var(--fs-color-x) / alpha)` — that resolves to a token and is the correct pattern.
const COLOR_LITERAL_RE = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(\s*[\d.]/;
const COLOR_LITERAL_RE_G = /#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?)\(\s*[\d.]/g;

// ---------------------------------------------------------------------------
// path helpers
// ---------------------------------------------------------------------------

function relKey(absPath) {
  return relative(WEB_ROOT, absPath).split(sep).join('/');
}

function inScope(rel) {
  if (!rel.startsWith('src/app/')) return false;
  if (!(rel.endsWith('.html') || rel.endsWith('.scss'))) return false;
  return !EXEMPT_PREFIXES.some(p => rel.startsWith(p));
}

function lineAt(text, index) {
  let line = 1;
  for (let i = 0; i < index && i < text.length; i++) if (text[i] === '\n') line++;
  return line;
}

// Replace matched spans with blanks but keep newlines, so reported line numbers stay accurate.
function blankOut(text, regex) {
  return text.replace(regex, m => m.replace(/[^\n]/g, ' '));
}

// ---------------------------------------------------------------------------
// scanners — each returns [{ rule, line }]
// ---------------------------------------------------------------------------

function classifyTag(name, attrs) {
  const n = name.toLowerCase();
  if (n === 'button') return 'R1';
  if (n === 'input') return 'R2';
  if (n === 'select') return 'R3';
  if (n === 'textarea') return 'R4';
  if (n === 'table') return 'R5';
  if (n === 'svg' || n === 'iconify-icon') return 'R6';
  if (n === 'i' && /\bclass\s*=/.test(attrs)) return 'R6';
  if (n.startsWith('mat-')) return 'R7';
  if (n.startsWith('dx-')) return 'R8';
  return null;
}

function scanHtml(rawText) {
  const violations = [];
  // Strip comments first (keep newlines) so commented-out markup never trips the guard.
  const text = blankOut(rawText, /<!--[\s\S]*?-->/g);

  // Element scan. The attr group tolerates quoted values containing '>'.
  const tagRe = /<([a-zA-Z][a-zA-Z0-9-]*)((?:"[^"]*"|'[^']*'|[^>"'])*?)\/?>/g;
  let m;
  while ((m = tagRe.exec(text)) !== null) {
    const rule = classifyTag(m[1], m[2]);
    if (rule) violations.push({ rule, line: lineAt(text, m.index) });
  }

  // R9 — colour literals inside style attributes / [style.*] / [ngStyle] bindings only.
  // A binding to a function (e.g. [style.background-color]="projectColorHex(id)") has no
  // literal colour, so it is correctly ignored.
  const styleAttrRe = /(?:\[(?:style(?:\.[^\]]*)?|ngStyle)\]|style)\s*=\s*("[^"]*"|'[^']*')/gi;
  while ((m = styleAttrRe.exec(text)) !== null) {
    if (COLOR_LITERAL_RE.test(m[1])) violations.push({ rule: 'R9', line: lineAt(text, m.index) });
  }

  // R10 — provenance.
  while ((m = PROVENANCE_RE.exec(text)) !== null) {
    violations.push({ rule: 'R10', line: lineAt(text, m.index) });
  }
  PROVENANCE_RE.lastIndex = 0;

  return violations;
}

function scanScss(rawText) {
  const violations = [];
  let text = blankOut(rawText, /\/\*[\s\S]*?\*\//g); // block comments
  text = blankOut(text, /\/\/[^\n]*/g);              // line comments

  let m;
  while ((m = COLOR_LITERAL_RE_G.exec(text)) !== null) {
    violations.push({ rule: 'R9', line: lineAt(text, m.index) });
  }
  COLOR_LITERAL_RE_G.lastIndex = 0;

  while ((m = PROVENANCE_RE.exec(text)) !== null) {
    violations.push({ rule: 'R10', line: lineAt(text, m.index) });
  }
  PROVENANCE_RE.lastIndex = 0;

  return violations;
}

// Scan one absolute path. Returns { rel, violations } or null if out of scope / missing.
function scanFile(absPath) {
  const rel = relKey(absPath);
  if (!inScope(rel)) return null;
  if (!existsSync(absPath)) return null;
  const text = readFileSync(absPath, 'utf8');
  const violations = rel.endsWith('.scss') ? scanScss(text) : scanHtml(text);
  return { rel, violations };
}

// ---------------------------------------------------------------------------
// baseline ratchet
// ---------------------------------------------------------------------------

function loadBaseline() {
  if (!existsSync(BASELINE_PATH)) return {};
  try {
    return JSON.parse(readFileSync(BASELINE_PATH, 'utf8')).files ?? {};
  } catch {
    return {};
  }
}

function countByRule(violations) {
  const counts = {};
  for (const v of violations) counts[v.rule] = (counts[v.rule] ?? 0) + 1;
  return counts;
}

// Given current violations for a file and its baseline counts, return the subset that is NEW
// (count for a rule exceeds the grandfathered baseline). Reports the highest-line instances.
function newViolations(violations, baselineCounts) {
  const byRule = {};
  for (const v of violations) (byRule[v.rule] ??= []).push(v);
  const out = [];
  for (const [rule, list] of Object.entries(byRule)) {
    const allowed = baselineCounts?.[rule] ?? 0;
    const excess = list.length - allowed;
    if (excess > 0) out.push(...list.slice(-excess)); // newest (latest-line) instances
  }
  return out.sort((a, b) => a.line - b.line);
}

// ---------------------------------------------------------------------------
// directory walk
// ---------------------------------------------------------------------------

function walk(dir, out = []) {
  if (!existsSync(dir)) return out;
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const full = join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else if (entry.isFile() && (entry.name.endsWith('.html') || entry.name.endsWith('.scss'))) out.push(full);
  }
  return out;
}

// ---------------------------------------------------------------------------
// reporting
// ---------------------------------------------------------------------------

function report(blocking, bannedDeps = []) {
  const lines = [];
  lines.push('fs-guard: shared-component discipline violations\n');
  for (const { rel, items } of blocking) {
    lines.push(rel);
    for (const v of items) {
      lines.push(`  L${String(v.line).padEnd(4)} ${v.rule.padEnd(3)} ${RULE_FIX[v.rule]}`);
    }
    lines.push('');
  }
  for (const d of bannedDeps) {
    lines.push(`package.json (${d.section})  R11  banned grid library "${d.name}" — ${RULE_FIX.R11}. See Babesiosis.Web/rules/data-tables.md.`);
  }
  if (bannedDeps.length) lines.push('');
  lines.push('');
  lines.push('These are NEW violations (beyond the grandfathered baseline). Fix them with the');
  lines.push('listed fs-* component — or, if this file is legitimately shell/legacy code, add');
  lines.push('its prefix to EXEMPT_PREFIXES in scripts/fs-guard.mjs. See Babesiosis.Web/rules/');
  lines.push('shared-components.md (banned-in-features table).');
  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// modes
// ---------------------------------------------------------------------------

function runFiles(paths) {
  const baseline = loadBaseline();
  const blocking = [];
  let touchedPackageJson = false;
  for (const p of paths) {
    const abs = resolve(process.cwd(), p);
    if (abs === PACKAGE_JSON) touchedPackageJson = true;
    const scanned = scanFile(abs);
    if (!scanned) continue;
    const items = newViolations(scanned.violations, baseline[scanned.rel]);
    if (items.length) blocking.push({ rel: scanned.rel, items });
  }
  // R11 only when package.json is one of the edited paths — so unrelated edits never
  // trip on a dependency the committer didn't touch (there are none today regardless).
  const bannedDeps = touchedPackageJson ? checkBannedGridDeps() : [];
  if (blocking.length || bannedDeps.length) {
    process.stderr.write(report(blocking, bannedDeps) + '\n');
    process.exit(2);
  }
  process.exit(0);
}

function runAll({ updateBaseline = false } = {}) {
  const files = walk(APP_DIR).map(relKey).filter(inScope).sort();
  const baseline = loadBaseline();
  const blocking = [];
  const snapshot = {};
  let totalCurrent = 0;

  for (const rel of files) {
    const scanned = scanFile(join(WEB_ROOT, rel));
    if (!scanned || !scanned.violations.length) continue;
    totalCurrent += scanned.violations.length;
    snapshot[rel] = countByRule(scanned.violations);
    if (!updateBaseline) {
      const items = newViolations(scanned.violations, baseline[rel]);
      if (items.length) blocking.push({ rel, items });
    }
  }

  const bannedDeps = updateBaseline ? [] : checkBannedGridDeps();

  if (updateBaseline) {
    writeFileSync(
      BASELINE_PATH,
      JSON.stringify(
        { _comment: 'Grandfathered fs-guard violations. Regenerate with: npm run lint:fs:baseline. Counts may only go DOWN.', generated: new Date().toISOString(), files: snapshot },
        null, 2,
      ) + '\n',
    );
    const fileCount = Object.keys(snapshot).length;
    process.stdout.write(`fs-guard: baseline written — ${totalCurrent} grandfathered violation(s) across ${fileCount} file(s).\n`);
    process.exit(0);
  }

  if (blocking.length || bannedDeps.length) {
    process.stderr.write(report(blocking, bannedDeps) + '\n');
    process.exit(2);
  }
  process.stdout.write(`fs-guard: clean — no new violations beyond baseline (${totalCurrent} grandfathered).\n`);
  process.exit(0);
}

// ---------------------------------------------------------------------------
// entry
// ---------------------------------------------------------------------------

const args = process.argv.slice(2);
if (args.includes('--update-baseline')) {
  runAll({ updateBaseline: true });
} else if (args.includes('--all')) {
  runAll();
} else if (args.length) {
  runFiles(args);
} else {
  process.stderr.write('usage: fs-guard.mjs <path...> | --all | --update-baseline\n');
  process.exit(1);
}
