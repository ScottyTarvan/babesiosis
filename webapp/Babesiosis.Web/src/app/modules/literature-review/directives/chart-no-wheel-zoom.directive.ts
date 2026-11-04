import { DestroyRef, Directive, ElementRef, inject } from '@angular/core';

/**
 * Stops the mouse wheel from zooming an ApexCharts chart inside the host.
 *
 * Apex zooms a line chart's x-axis on the wheel by default, and the gnome-ui
 * wrappers don't expose `chart.zoom`, so a reader scrolling the page past the
 * chart shrinks and stretches it instead. The wheel event is stopped on the
 * host in the capture phase, before it reaches Apex's own listener. It is not
 * cancelled, so the page still scrolls as normal.
 */
@Directive({
  selector: '[fsChartNoWheelZoom]',
  standalone: true,
})
export class ChartNoWheelZoomDirective {
  constructor() {
    const host = inject<ElementRef<HTMLElement>>(ElementRef).nativeElement;
    const stop = (event: WheelEvent): void => event.stopPropagation();
    host.addEventListener('wheel', stop, { capture: true, passive: true });
    inject(DestroyRef).onDestroy(() => host.removeEventListener('wheel', stop, { capture: true }));
  }
}
