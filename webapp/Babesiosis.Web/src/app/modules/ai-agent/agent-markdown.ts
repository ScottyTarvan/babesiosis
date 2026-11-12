import { ChatCitationViewModel } from 'app/modules/ai-agent/viewmodels/chat-message.viewmodel';

/**
 * A review code as the agent cites it, e.g. CB024 (the server's `ArticleCode` regex).
 * `S-CB050` is a dataset code, not a citation of the article CB050.
 */
const ARTICLE_CODE = String.raw`(?<!\bS-)\b[A-Z]{2}\d{3}\b`;

/** A bracketed group that is not a Markdown link: [CB001], [CB001, CB024], [CB004 Results], [SY05]. */
const BRACKET_GROUP = /\[([^\]\[]+)\](?!\()/g;

/**
 * A source inside the app that an answer cites by code: an experiment
 * (`[SV-05-01-age-death]`) or a page of the clinical manual (`[SY05]`).
 */
export interface AgentAppLink {
  /** The code as the agent cites it. */
  code: string;
  /** Other spellings the agent may use, e.g. the short form `SV-05-01`. */
  aliases?: readonly string[];
  /** Where the source is shown in the app, relative to the base href, e.g. `experiments/SV-05-01-age-death`. */
  href: string;
  /** The tooltip: the experiment's name or the page's title. */
  title: string;
}

/** Options for {@link renderAgentMarkdown}. */
export interface MarkdownRenderOptions {
  /**
   * The experiments and clinical pages the answer cites. A citation of one becomes a link
   * that opens in a new tab, so the conversation stays on screen.
   */
  appLinks?: readonly AgentAppLink[];
  /**
   * Renders a link whose target is not http(s), such as `[CB001](articles/CB001_….md)`,
   * and returns the HTML to put in its place. It must escape what it inserts
   * (`escapeHtml`). Without it such links are left as written.
   */
  resolveLink?: (label: string, href: string) => string;
}

/**
 * Renders an agent answer (Markdown) to HTML for `[innerHTML]`.
 *
 * A small subset, the one the agent writes: paragraphs, headings, bullet and
 * numbered lists, tables, fenced and inline code, bold, italics, http(s) links
 * and rules. Every piece of model text is HTML-escaped before markup is added,
 * and Angular's sanitizer still runs over the result.
 *
 * Citations such as `[CB024]` become links to the article's source when the
 * server resolved one, so a claim can be checked in one click. Codes the server
 * did not resolve (not in the database) stay as plain text. Citations of an
 * experiment or a clinical manual page (`options.appLinks`) become links to
 * their screen in the app.
 */
export function renderAgentMarkdown(
  markdown: string,
  citations: readonly ChatCitationViewModel[] = [],
  options: MarkdownRenderOptions = {},
): string {
  const sources = citationSources(citations, options.appLinks ?? []);
  const inline = (text: string) => renderInline(text, sources, options);

  const out: string[] = [];
  let paragraph: string[] = [];
  let list: { type: 'ul' | 'ol'; items: string[] } | null = null;
  let table: string[] = [];
  let fence: string[] | null = null;

  const flushParagraph = () => {
    if (paragraph.length) {
      out.push(`<p>${inline(paragraph.join(' '))}</p>`);
      paragraph = [];
    }
  };
  const flushList = () => {
    if (list) {
      out.push(`<${list.type}>${list.items.map(item => `<li>${inline(item)}</li>`).join('')}</${list.type}>`);
      list = null;
    }
  };
  const flushTable = () => {
    if (table.length) {
      out.push(renderTable(table, inline));
      table = [];
    }
  };
  const flushAll = () => {
    flushParagraph();
    flushList();
    flushTable();
  };

  for (const line of (markdown ?? '').replace(/\r\n?/g, '\n').split('\n')) {
    if (fence) {
      if (/^\s*```/.test(line)) {
        out.push(`<pre><code>${escapeHtml(fence.join('\n'))}</code></pre>`);
        fence = null;
      } else {
        fence.push(line);
      }
      continue;
    }

    if (/^\s*```/.test(line)) {
      flushAll();
      fence = [];
      continue;
    }

    if (/^\s*\|.*\|\s*$/.test(line)) {
      flushParagraph();
      flushList();
      table.push(line);
      continue;
    }
    flushTable();

    if (/^\s*$/.test(line)) {
      flushAll();
      continue;
    }

    // Headings sit inside a chat bubble, so # starts at h3.
    const heading = /^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$/.exec(line);
    if (heading) {
      flushAll();
      const level = Math.min(heading[1].length + 2, 6);
      out.push(`<h${level}>${inline(heading[2])}</h${level}>`);
      continue;
    }

    if (/^\s{0,3}([-*_])(\s*\1){2,}\s*$/.test(line)) {
      flushAll();
      out.push('<hr>');
      continue;
    }

    const bullet = /^\s*[-*+]\s+(.*)$/.exec(line);
    const numbered = /^\s*\d+[.)]\s+(.*)$/.exec(line);
    if (bullet || numbered) {
      flushParagraph();
      const type = bullet ? 'ul' : 'ol';
      if (list && list.type !== type) {
        flushList();
      }
      list ??= { type, items: [] };
      list.items.push((bullet ?? numbered)![1]);
      continue;
    }

    // An indented line under a list item continues that item.
    if (list && /^\s+\S/.test(line)) {
      list.items[list.items.length - 1] += ' ' + line.trim();
      continue;
    }

    flushList();
    paragraph.push(line.trim());
  }

  if (fence) {
    out.push(`<pre><code>${escapeHtml(fence.join('\n'))}</code></pre>`);
  }
  flushAll();
  return out.join('');
}

function renderTable(rows: string[], inline: (text: string) => string): string {
  const cells = (row: string) => row.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());
  const isSeparator = (row: string) => cells(row).every(c => /^:?-{1,}:?$/.test(c));

  const hasHeader = rows.length > 1 && isSeparator(rows[1]);
  const head = hasHeader ? `<thead><tr>${cells(rows[0]).map(c => `<th>${inline(c)}</th>`).join('')}</tr></thead>` : '';
  const body = (hasHeader ? rows.slice(2) : rows)
    .filter(row => !isSeparator(row))
    .map(row => `<tr>${cells(row).map(c => `<td>${inline(c)}</td>`).join('')}</tr>`)
    .join('');
  return `<table>${head}<tbody>${body}</tbody></table>`;
}

/**
 * Inline markup. Code spans, links and citations are rendered first and parked
 * in slots, so the emphasis rules never reach inside them; everything else is
 * escaped before emphasis is applied.
 */
function renderInline(text: string, sources: CitationSources, options: MarkdownRenderOptions): string {
  const slots: string[] = [];
  const park = (html: string) => `\u0000${slots.push(html) - 1}\u0000`;

  let s = text.replace(/\u0000/g, '');
  s = s.replace(/`([^`]+)`/g, (_, code: string) => park(`<code>${escapeHtml(code)}</code>`));
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (_, label: string, url: string) =>
    park(`<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`));
  const resolveLink = options.resolveLink;
  if (resolveLink) {
    s = s.replace(/\[([^\]]+)\]\(([^\s)]+)\)/g, (_, label: string, href: string) => park(resolveLink(label, href)));
  }
  s = s.replace(BRACKET_GROUP, (whole: string, inner: string) => {
    const html = renderCitationGroup(inner, sources);
    return html === null ? whole : park(html);
  });

  s = escapeHtml(s);
  s = s.replace(/\*\*(?=\S)(.+?)(?<=\S)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/__(?=\S)(.+?)(?<=\S)__/g, '<strong>$1</strong>');
  s = s.replace(/(^|[^*\w])\*(?=\S)(.+?)(?<=\S)\*(?![*\w])/g, '$1<em>$2</em>');
  s = s.replace(/(^|[^_\w])_(?=\S)(.+?)(?<=\S)_(?![_\w])/g, '$1<em>$2</em>');

  return s.replace(/\u0000(\d+)\u0000/g, (_, i: string) => slots[Number(i)]);
}

/** What a code inside a bracketed group can cite. */
interface CitationSources {
  articles: Map<string, ChatCitationViewModel>;
  /** Experiments and clinical pages, by code and by alias. */
  app: Map<string, AgentAppLink>;
  /** Matches an app code or alias (longest first), or something shaped like an article code. */
  pattern: RegExp;
}

function citationSources(citations: readonly ChatCitationViewModel[], appLinks: readonly AgentAppLink[]): CitationSources {
  const app = new Map<string, AgentAppLink>();
  for (const link of appLinks) {
    for (const code of [link.code, ...(link.aliases ?? [])]) {
      if (code && !app.has(code)) {
        app.set(code, link);
      }
    }
  }

  // Longest first, and not inside a longer code: SV-05-01 must not match in SV-05-01-age-death.
  const codes = [...app.keys()].sort((a, b) => b.length - a.length).map(escapeRegExp);
  const appCode = codes.length ? String.raw`(?<![\w-])(?:${codes.join('|')})(?![\w-])|` : '';

  return {
    articles: new Map(citations.map(c => [c.code.toUpperCase(), c])),
    app,
    pattern: new RegExp(appCode + ARTICLE_CODE, 'g'),
  };
}

/** The group as HTML, or null when it holds no code and so is not a citation. */
function renderCitationGroup(inner: string, sources: CitationSources): string | null {
  let html = '';
  let last = 0;
  let found = false;
  for (const match of inner.matchAll(sources.pattern)) {
    found = true;
    html += escapeHtml(inner.slice(last, match.index));
    const appLink = sources.app.get(match[0]);
    html += appLink ? renderAppLink(match[0], appLink) : renderCitation(match[0], sources.articles.get(match[0]));
    last = match.index! + match[0].length;
  }
  if (!found) {
    return null;
  }
  html += escapeHtml(inner.slice(last));
  return `<span class="agent-cite">[${html}]</span>`;
}

function renderAppLink(code: string, link: AgentAppLink): string {
  return `<a href="${escapeHtml(link.href)}" target="_blank" rel="noopener" title="${escapeHtml(link.title)}">${escapeHtml(code)}</a>`;
}

function escapeRegExp(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function renderCitation(code: string, citation: ChatCitationViewModel | undefined): string {
  if (!citation) {
    return code;
  }
  const title = escapeHtml(citation.year ? `${citation.title} (${citation.year})` : citation.title);
  if (citation.sourceUrl) {
    return `<a href="${escapeHtml(citation.sourceUrl)}" target="_blank" rel="noopener noreferrer" title="${title}">${code}</a>`;
  }
  return `<abbr title="${title}">${code}</abbr>`;
}

export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
