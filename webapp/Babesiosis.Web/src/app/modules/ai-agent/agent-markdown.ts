import { ChatCitationViewModel } from 'app/modules/ai-agent/viewmodels/chat-message.viewmodel';

/** A review code as the agent cites it, e.g. CB024 (the server's `ArticleCode` regex). */
const ARTICLE_CODE = /\b[A-Z]{2}\d{3}\b/g;

/** A bracketed group holding at least one code: [CB001], [CB001, CB024], [CB004 Results]. */
const CITATION_GROUP = /\[([^\]\[]*\b[A-Z]{2}\d{3}\b[^\]\[]*)\](?!\()/g;

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
 * did not resolve (not in the database) stay as plain text.
 */
export function renderAgentMarkdown(markdown: string, citations: readonly ChatCitationViewModel[] = []): string {
  const byCode = new Map(citations.map(c => [c.code.toUpperCase(), c]));
  const inline = (text: string) => renderInline(text, byCode);

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
function renderInline(text: string, byCode: Map<string, ChatCitationViewModel>): string {
  const slots: string[] = [];
  const park = (html: string) => `\u0000${slots.push(html) - 1}\u0000`;

  let s = text.replace(/\u0000/g, '');
  s = s.replace(/`([^`]+)`/g, (_, code: string) => park(`<code>${escapeHtml(code)}</code>`));
  s = s.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, (_, label: string, url: string) =>
    park(`<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`));
  s = s.replace(CITATION_GROUP, (_, inner: string) => park(renderCitationGroup(inner, byCode)));

  s = escapeHtml(s);
  s = s.replace(/\*\*(?=\S)(.+?)(?<=\S)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/__(?=\S)(.+?)(?<=\S)__/g, '<strong>$1</strong>');
  s = s.replace(/(^|[^*\w])\*(?=\S)(.+?)(?<=\S)\*(?![*\w])/g, '$1<em>$2</em>');
  s = s.replace(/(^|[^_\w])_(?=\S)(.+?)(?<=\S)_(?![_\w])/g, '$1<em>$2</em>');

  return s.replace(/\u0000(\d+)\u0000/g, (_, i: string) => slots[Number(i)]);
}

function renderCitationGroup(inner: string, byCode: Map<string, ChatCitationViewModel>): string {
  let html = '';
  let last = 0;
  for (const match of inner.matchAll(ARTICLE_CODE)) {
    html += escapeHtml(inner.slice(last, match.index));
    html += renderCitation(match[0], byCode.get(match[0]));
    last = match.index! + match[0].length;
  }
  html += escapeHtml(inner.slice(last));
  return `<span class="agent-cite">[${html}]</span>`;
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

function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
