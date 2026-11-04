import {
  afterNextRender,
  ChangeDetectionStrategy,
  Component,
  ComponentRef,
  DestroyRef,
  Directive,
  effect,
  ElementRef,
  inject,
  input,
  ViewContainerRef,
} from '@angular/core';
import { FsTooltipDirective, FsTooltipPlacement } from '@core';

/** Which of the chart's labels get the tooltip. */
export type ChartLabelTitlesTarget = 'y-axis' | 'legend';

interface TargetConfig {
  /** The element hovered: one per label. */
  label: string;
  /** The element inside it whose text is looked up in the map. */
  text: string;
  placement: FsTooltipPlacement;
}

const TARGETS: Record<ChartLabelTitlesTarget, TargetConfig> = {
  'y-axis': { label: '.apexcharts-yaxis-label', text: 'tspan', placement: 'right' },
  // The whole legend item, so hovering the colour marker counts too.
  'legend': { label: '.apexcharts-legend-series', text: '.apexcharts-legend-text', placement: 'top' },
};

/**
 * An invisible box laid over the hovered label, carrying the gnome-ui
 * tooltip. `fsTooltip` only works as a template directive, and Apex draws the
 * labels itself, so the tooltip anchors to this box instead of the label.
 */
@Component({
  selector: 'fs-chart-label-tooltip-anchor',
  standalone: true,
  imports: [FsTooltipDirective],
  template: `<span class="anchor" [fsTooltip]="text()" [fsTooltipPlacement]="placement()"></span>`,
  styles: `
    :host { position: fixed; pointer-events: none; }
    .anchor { display: block; width: 100%; height: 100%; }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
class ChartLabelTooltipAnchorComponent {
  readonly text = input<string>('');
  readonly placement = input<FsTooltipPlacement>('right');
}

/**
 * Gives each y-axis label, or each legend item, of an ApexCharts chart inside
 * the host a gnome-ui tooltip, looked up by the label's text:
 * `{ ERY: 'Haemolysis' }` shows "Haemolysis" when hovering "ERY". Labels with
 * no entry keep Apex's own behaviour.
 *
 * The gnome-ui chart wrappers expose neither the axes, the legend nor the
 * chart events, so hovers are caught by delegation on the host, and the native
 * `<title>` Apex renders on a mapped y-axis label is removed whenever Apex
 * redraws (data change, resize, theme flip) so the browser's own tooltip
 * doesn't show as well.
 */
@Directive({
  selector: '[fsChartLabelTitles]',
  standalone: true,
  host: {
    '(mouseover)': 'onMouseOver($event)',
    '(mouseout)': 'onMouseOut($event)',
  },
})
export class ChartLabelTitlesDirective {
  readonly fsChartLabelTitles = input<Readonly<Record<string, string>>>({});
  readonly fsChartLabelTitlesTarget = input<ChartLabelTitlesTarget>('y-axis');

  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  private readonly viewContainer = inject(ViewContainerRef);
  private anchor: ComponentRef<ChartLabelTooltipAnchorComponent> | null = null;
  private activeLabel: Element | null = null;

  constructor() {
    const observer = new MutationObserver(() => this.apply());
    afterNextRender(() => observer.observe(this.host.nativeElement, { childList: true, subtree: true }));
    inject(DestroyRef).onDestroy(() => observer.disconnect());

    effect(() => this.apply());
  }

  private get target(): TargetConfig {
    return TARGETS[this.fsChartLabelTitlesTarget()];
  }

  protected onMouseOver(event: MouseEvent): void {
    const label = (event.target as Element).closest(this.target.label);
    if (label === this.activeLabel) {
      return;
    }
    this.hide();
    const text = label && this.textFor(label);
    if (label && text) {
      this.show(label, text);
    }
  }

  protected onMouseOut(event: MouseEvent): void {
    // Moving between a label's own children is not leaving it.
    if (this.activeLabel && !this.activeLabel.contains(event.relatedTarget as Node | null)) {
      this.hide();
    }
  }

  private show(label: Element, text: string): void {
    this.anchor ??= this.viewContainer.createComponent(ChartLabelTooltipAnchorComponent);
    this.anchor.setInput('text', text);
    this.anchor.setInput('placement', this.target.placement);
    // Bind the inputs now: the tooltip reads them the moment it is told to show.
    this.anchor.changeDetectorRef.detectChanges();

    const rect = label.getBoundingClientRect();
    const box = this.anchor.location.nativeElement as HTMLElement;
    Object.assign(box.style, {
      left: `${rect.left}px`,
      top: `${rect.top}px`,
      width: `${rect.width}px`,
      height: `${rect.height}px`,
    });
    this.activeLabel = label;
    this.tooltipHost()?.dispatchEvent(new MouseEvent('mouseenter'));
  }

  private hide(): void {
    if (this.activeLabel) {
      this.activeLabel = null;
      this.tooltipHost()?.dispatchEvent(new MouseEvent('mouseleave'));
    }
  }

  /** The element `fsTooltip` listens on; the anchor has no pointer events of its own. */
  private tooltipHost(): Element | null {
    return (this.anchor?.location.nativeElement as HTMLElement | undefined)?.querySelector('.anchor') ?? null;
  }

  private textFor(label: Element): string | undefined {
    const key = label.querySelector(this.target.text)?.textContent?.trim() ?? '';
    return this.fsChartLabelTitles()[key];
  }

  private apply(): void {
    // A redraw replaces the labels, and the one under the pointer never sees a mouseout.
    if (this.activeLabel && !this.activeLabel.isConnected) {
      this.hide();
    }
    this.host.nativeElement.querySelectorAll(this.target.label).forEach(label => {
      // Only remove on a match: the removal is itself a mutation the observer sees.
      if (this.textFor(label)) {
        label.querySelector('title')?.remove();
      }
    });
  }
}
