/**
 * Help & Support content model (spec `platform/help-support.md` §3.6).
 *
 * The outline lives in one index file (`content/help-index.ts`) as metadata
 * only; each topic's body lives in its own small chunk file and is loaded
 * lazily when the topic is opened. An agent keeping help in sync reads the
 * index to find a topic, then edits exactly one chunk (§3.7).
 */

export type HelpModuleStatus = 'implemented' | 'in-progress' | 'planned';

/** One block of a topic body. Kept deliberately small so a chunk stays plain
 *  data an agent can edit without touching the renderer. */
export type HelpBlock =
  | { kind: 'paragraph'; text: string }
  | { kind: 'heading'; text: string }
  | { kind: 'list'; items: string[] }
  | { kind: 'note'; intent: 'info' | 'warning'; text: string };

/** What a chunk file exports as its default: the body of exactly one topic. */
export interface HelpTopicBody {
  blocks: HelpBlock[];
}

export interface HelpTopicEntry {
  key: string;
  title: string;
  summary: string;
  /** Specification documents the topic is written from (paths under
   *  `.claude/specs/`). Data only — never rendered (§3.6, R3). */
  specRefs: string[];
  /** Repo-relative path to the topic's chunk file. */
  chunk: string;
  load: () => Promise<HelpTopicBody>;
}

export interface HelpSection {
  key: string;
  label: string;
  topics: HelpTopicEntry[];
}

export interface HelpModule {
  key: string;
  label: string;
  icon: string;
  status: HelpModuleStatus;
  summary: string;
  sections: HelpSection[];
}
