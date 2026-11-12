import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { FsShell } from '@layouts/fs-shell';
import { homeUrl } from '@layouts/constants';
import { helpUrlMatcher } from 'app/modules/help/help.routes';
import { experimentsUrlMatcher } from 'app/modules/experiments/experiments.routes';
import { clinicalUrlMatcher } from 'app/modules/clinical/clinical.routes';

const routes: Routes = [
  {
    path: '',
    component: FsShell,
    children: [
      { path: '', redirectTo: homeUrl, pathMatch: 'full' },
      {
        // The landing page (homeUrl): the overview of the canine literature.
        path: 'home',
        loadComponent: () =>
          import('app/modules/home/home.component').then(m => m.HomeComponent),
      },
      // The old Literature Review dashboard was replaced by the overview; keep its links working.
      { path: 'literature-review', redirectTo: homeUrl, pathMatch: 'full' },
      // /topics opens the first topic (ERY, sort order 1); the page has a topic switcher.
      { path: 'topics', redirectTo: 'topics/ERY', pathMatch: 'full' },
      {
        // One page per category; the router reuses the component when the code changes.
        path: 'topics/:code',
        loadComponent: () =>
          import('app/modules/topics/topic.component').then(m => m.TopicComponent),
      },
      {
        path: 'gaps',
        loadComponent: () =>
          import('app/modules/gaps/gaps.component').then(m => m.GapsComponent),
      },
      {
        path: 'reference-articles',
        loadComponent: () =>
          import('app/modules/reference-articles/reference-articles.component').then(m => m.ReferenceArticlesComponent),
      },
      {
        // /experiments and /experiments/:code — one config so the list panel keeps
        // its scroll and search when another experiment is picked.
        matcher: experimentsUrlMatcher,
        loadComponent: () =>
          import('app/modules/experiments/experiments.component').then(m => m.ExperimentsComponent),
      },
      {
        // /clinical and /clinical/:id — one config so the rail keeps its filter
        // and scroll when another page of the manual is picked.
        matcher: clinicalUrlMatcher,
        loadComponent: () =>
          import('app/modules/clinical/clinical.component').then(m => m.ClinicalComponent),
      },
      {
        // Chat screen only; the agent behind it is connected in phase two.
        path: 'ai-agent',
        loadComponent: () =>
          import('app/modules/ai-agent/ai-agent.component').then(m => m.AiAgentComponent),
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

