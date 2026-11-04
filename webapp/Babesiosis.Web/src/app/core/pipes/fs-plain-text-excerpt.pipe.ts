import { Pipe, PipeTransform } from '@angular/core';
import { plainTextFromHtml } from '@fundstream-ai/gnome-ui/rich-editor';

/**
 * Renders rich (HTML) description content as a plain-text excerpt for table cells:
 * strips all markup to visible text, collapses whitespace, and optionally truncates
 * with an ellipsis. Never emits HTML, so cells stay safe and free of `[innerHTML]`.
 *
 * `{{ row.description | fsPlainTextExcerpt:120 }}`
 */
@Pipe({ name: 'fsPlainTextExcerpt', standalone: true })
export class FsPlainTextExcerptPipe implements PipeTransform {
  transform(html: string | null | undefined, maxLength?: number): string {
    const text = plainTextFromHtml(html);
    if (maxLength && maxLength > 0 && text.length > maxLength) {
      return `${text.slice(0, maxLength).trimEnd()}…`;
    }
    return text;
  }
}
