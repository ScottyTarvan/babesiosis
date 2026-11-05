import { ChangeDetectionStrategy, Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { FsBannerComponent, FsCardComponent, FsPageHeaderComponent, FsSymbolComponent } from '@core';
import { MENU, type MenuItem } from '@layouts/menu-meta';

/**
 * The landing page: the shell's '' redirect (`homeUrl`) sends every visitor here.
 *
 * Placeholder for now: a welcome card and a link to each screen in the menu.
 * The real home content (summary figures, recent activity) comes later.
 */
@Component({
  selector: 'fs-home',
  standalone: true,
  imports: [RouterLink, FsBannerComponent, FsCardComponent, FsPageHeaderComponent, FsSymbolComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  /** Every menu link except Home itself, in menu order: the screens a visitor can go to. */
  protected readonly screens: readonly MenuItem[] = MENU.filter(item => !!item.link && item.key !== 'home');
}
