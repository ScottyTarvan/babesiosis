import { escapeHtml, renderAgentMarkdown } from 'app/modules/ai-agent/agent-markdown';
import { articleUrl } from 'app/modules/review/review-links';

/** `articles/CB001_2017_….md`, the synthesis files' link to an article note. */
const ARTICLE_NOTE = /^(?:\.\/)?articles\/([A-Z]{2}\d{3})(?:[_.]|$)/;

/** The class an in-app link carries, so `SynthesisTextComponent` routes it instead of reloading the page. */
export const APP_LINK_CLASS = 'fs-synthesis-app-link';

/**
 * Renders a synthesis section (Markdown, as written in core/search/synthesis) to HTML for
 * `[innerHTML]`, with the agent answer renderer (`renderAgentMarkdown`): the same escaping,
 * and Angular's sanitizer still runs over the result.
 *
 * The files link to the review's own files, which do not exist in the app. A link to an
 * article note becomes an in-app link to that article in the Articles grid, by code. Every
 * other relative link (datasets.md, search-log.md, cohorts.json, #anchors) is shown as its
 * label, as plain text. http(s) links open in a new window, as in agent answers.
 */
export function renderSynthesisMarkdown(markdown: string): string {
  return renderAgentMarkdown(markdown, [], {
    resolveLink: (label, href) => {
      const article = ARTICLE_NOTE.exec(href);
      if (article) {
        const code = article[1];
        return `<a class="${APP_LINK_CLASS}" href="${escapeHtml(articleUrl(code))}" title="Open ${code} in the article list">${escapeHtml(label)}</a>`;
      }
      return escapeHtml(label);
    },
  });
}
