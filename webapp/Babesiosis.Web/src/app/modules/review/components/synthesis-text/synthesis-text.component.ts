import { ChangeDetectionStrategy, Component, computed, inject, input } from '@angular/core';
import { Router } from '@angular/router';
import { APP_LINK_CLASS, renderSynthesisMarkdown } from 'app/modules/review/synthesis-markdown';

/**
 * One synthesis section's text, rendered from Markdown as written. Article links inside it
 * are in-app links: a click is routed (no page reload); a modified click (new tab) is left
 * to the browser.
 */
@Component({
  selector: 'fs-synthesis-text',
  standalone: true,
  templateUrl: './synthesis-text.component.html',
  styleUrls: ['./synthesis-text.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: { '(click)': 'onClick($event)' },
})
export class SynthesisTextComponent {
  private readonly router = inject(Router);

  /** The section body, Markdown. */
  readonly markdown = input.required<string>();

  protected readonly html = computed(() => renderSynthesisMarkdown(this.markdown()));

  protected onClick(event: MouseEvent): void {
    if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) {
      return;
    }
    const link = (event.target as HTMLElement | null)?.closest?.(`a.${APP_LINK_CLASS}`);
    const href = link?.getAttribute('href');
    if (href?.startsWith('/')) {
      event.preventDefault();
      void this.router.navigateByUrl(href);
    }
  }
}
