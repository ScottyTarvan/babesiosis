import { DestroyRef, Directive, ElementRef, inject, Input } from '@angular/core';

/**
 * Gives matching elements in the same grid row the same height.
 *
 * The dashboard grid holds one card per cell, and each card ends with a summary
 * panel that sizes to its text. Two cards side by side share a height (the grid
 * stretches them) but their panels wrap to different line counts, so one panel's
 * top border sits a line above the other's. CSS cannot share a height across
 * separate cards, so this directive measures: it clears any min-height it set,
 * groups the matching elements by the top edge of the grid cell that holds them,
 * and sets every element's min-height to the tallest of its row. It re-runs on
 * any resize of the host and on any change to the host's subtree, because a
 * panel that appears after loading in a card whose neighbour already sets the
 * row height does not change the host's size.
 */
@Directive({
  selector: '[fsEqualRowHeights]',
  standalone: true,
})
export class EqualRowHeightsDirective {
  /** CSS selector of the elements to equalise within the host. */
  @Input({ required: true }) fsEqualRowHeights = '';

  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
  private timer: ReturnType<typeof setTimeout> | undefined;

  constructor() {
    const resizes = new ResizeObserver(() => this.schedule());
    resizes.observe(this.host);
    const mutations = new MutationObserver(() => this.schedule());
    mutations.observe(this.host, { childList: true, subtree: true });
    inject(DestroyRef).onDestroy(() => {
      resizes.disconnect();
      mutations.disconnect();
      clearTimeout(this.timer);
    });
  }

  // A coalesced timeout rather than requestAnimationFrame: frames are not
  // delivered while the document is hidden or throttled, a timeout still is.
  private schedule(): void {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.equalise(), 0);
  }

  private equalise(): void {
    if (!this.fsEqualRowHeights) return;
    const items = Array.from(this.host.querySelectorAll<HTMLElement>(this.fsEqualRowHeights));
    items.forEach(item => (item.style.minHeight = ''));

    const rows = new Map<number, HTMLElement[]>();
    for (const item of items) {
      const cell = Array.from(this.host.children).find(child => child.contains(item)) ?? item;
      const key = Math.round(cell.getBoundingClientRect().top);
      rows.set(key, [...(rows.get(key) ?? []), item]);
    }
    rows.forEach(group => {
      if (group.length < 2) return;
      const tallest = Math.max(...group.map(item => item.getBoundingClientRect().height));
      group.forEach(item => (item.style.minHeight = `${Math.ceil(tallest)}px`));
    });
  }
}
