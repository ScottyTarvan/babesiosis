import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FsSymbolComponent } from '@core';

@Component({
  selector: 'fs-shell-sidebar-item',
  standalone: true,
  imports: [RouterLink, FsSymbolComponent],
  templateUrl: './fs-shell-sidebar-item.html',
  styleUrls: ['./fs-shell-sidebar-item.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FsShellSidebarItem {
  readonly icon = input.required<string>();
  readonly label = input.required<string>();
  readonly path = input.required<string>();
  readonly active = input<boolean>(false);
  readonly collapsed = input<boolean>(false);

  protected readonly title = computed(() => this.collapsed() ? this.label() : null);
  protected readonly ariaLabel = computed(() => this.collapsed() ? this.label() : null);
}
