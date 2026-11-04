import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FsShell } from '@layouts/fs-shell';
import { homeUrl } from '@layouts/constants';
import { helpUrlMatcher } from 'app/modules/help/help.routes';

const routes: Routes = [
  {
    path: '',
    component: FsShell,
    children: [
      { path: '', redirectTo: homeUrl, pathMatch: 'full' },
      {
        // Placeholder until the Review screen is built in phase two.
        path: 'literature-review',
        loadComponent: () =>
          import('app/modules/literature-review/literature-review.component').then(m => m.LiteratureReviewComponent),
      },
      {
        path: 'reference-articles',
        loadComponent: () =>
          import('app/modules/reference-articles/reference-articles.component').then(m => m.ReferenceArticlesComponent),
      },
      // No /settings while the app has no sign-in: the page is account settings
      // only (profile, password, logout). SettingsModule is kept for when it returns.
      {
        // /help, /help/:module, /help/:module/:topic — one config so the
        // page is reused across topics (spec platform/help-support.md §3.9).
        matcher: helpUrlMatcher,
        loadComponent: () =>
          import('app/modules/help/help.component').then(m => m.HelpComponent),
      },
    ]
  }
];

@NgModule({
  imports: [
    CommonModule,
    RouterModule.forChild(routes),
    FsShell
  ]
})
export class LayoutModule { }

