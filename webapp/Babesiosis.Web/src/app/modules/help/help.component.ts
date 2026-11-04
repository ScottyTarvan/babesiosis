import {
  ChangeDetectionStrategy,
  Component,
  computed,
  effect,
  inject,
  signal,
} from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { ActivatedRoute, RouterLink } from '@angular/router';
import {
  FsBadgeComponent,
  FsBannerComponent,
  FsBreadcrumbItem,
  FsButtonComponent,
  FsCardComponent,
  FsEmptyStateComponent,
  FsFormFieldComponent,
  FsPageHeaderComponent,
  FsSymbolComponent,
  FsTextInputComponent,
  FsTextareaComponent,
  FsToastService,
} from '@core';
import { HELP_MODULES } from 'app/modules/help/content/help-index';
import {
  HelpModule,
  HelpSection,
  HelpTopicBody,
  HelpTopicEntry,
} from 'app/modules/help/help.viewmodel';

type HelpView = 'landing' | 'module' | 'topic' | 'not-found';

interface ActiveTopic {
  section: HelpSection;
  topic: HelpTopicEntry;
}

/**
 * Help & Support — an in-app documentation browser organised by FDM module
 * (spec `platform/help-support.md`). A navigation tree on the left, the
 * landing cards / module overview / topic article on the right.
 *
 * The outline comes from `content/help-index.ts`; a topic's body is loaded
 * from its own chunk only when the topic is opened (§3.6). The contact form
 * is shown on the landing page only (§3.3, §3.8); its send is simulated —
 * there is no support endpoint yet.
 */
@Component({
  selector: 'fs-help',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    FsBadgeComponent,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsEmptyStateComponent,
    FsFormFieldComponent,
    FsPageHeaderComponent,
    FsSymbolComponent,
    FsTextInputComponent,
    FsTextareaComponent,
  ],
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HelpComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly toast = inject(FsToastService);

  protected readonly modules = HELP_MODULES;

  // ---- Route state ---------------------------------------------------------
  private readonly params = toSignal(this.route.paramMap, { requireSync: true });
  protected readonly moduleKey = computed(() => this.params().get('module'));
  protected readonly topicKey = computed(() => this.params().get('topic'));

  protected readonly activeModule = computed<HelpModule | null>(() => {
    const key = this.moduleKey();
    return key ? this.modules.find(m => m.key === key) ?? null : null;
  });

  protected readonly activeTopic = computed<ActiveTopic | null>(() => {
    const module = this.activeModule();
    const key = this.topicKey();
    if (!module || !key) return null;
    for (const section of module.sections) {
      const topic = section.topics.find(t => t.key === key);
      if (topic) return { section, topic };
    }
    return null;
  });

  protected readonly view = computed<HelpView>(() => {
    if (!this.moduleKey()) return 'landing';
    if (!this.activeModule()) return 'not-found';
    if (!this.topicKey()) return 'module';
    return this.activeTopic() ? 'topic' : 'not-found';
  });

  // ---- Page header ---------------------------------------------------------
  protected readonly headerIcon = computed(() =>
    this.view() === 'not-found' ? 'help-circle' : this.activeModule()?.icon ?? 'help-circle');

  protected readonly headerTitle = computed(() => {
    switch (this.view()) {
      case 'topic': return this.activeTopic()!.topic.title;
      case 'module': return this.activeModule()!.label;
      default: return 'Help & Support';
    }
  });

  protected readonly breadcrumb = computed<FsBreadcrumbItem[]>(() => {
    const module = this.activeModule();
    const active = this.activeTopic();
    switch (this.view()) {
      case 'module':
        return [{ label: 'Help & Support', link: '/help' }, { label: module!.label }];
      case 'topic':
        return [
          { label: 'Help & Support', link: '/help' },
          { label: module!.label, link: `/help/${module!.key}` },
          { label: active!.section.label, link: `/help/${module!.key}` },
          { label: active!.topic.title },
        ];
      default:
        return [];
    }
  });

  protected readonly headerPlanned = computed(() =>
    this.view() !== 'not-found' && this.activeModule()?.status === 'planned');

  // ---- Topic body (lazy chunk) ---------------------------------------------
  protected readonly body = signal<HelpTopicBody | null>(null);
  private loadSeq = 0;

  // ---- Search / tree -------------------------------------------------------
  protected readonly searchControl = new FormControl<string>('', { nonNullable: true });
  protected readonly query = signal<string>('');
  protected readonly searching = computed(() => this.query().trim().length > 0);

  /** The tree, filtered to topics whose title or summary match the search
   *  (case-insensitive); modules and sections left empty drop out. */
  protected readonly tree = computed<readonly HelpModule[]>(() => {
    const q = this.query().trim().toLowerCase();
    if (!q) return this.modules;
    const matches = (t: HelpTopicEntry) =>
      t.title.toLowerCase().includes(q) || t.summary.toLowerCase().includes(q);
    return this.modules
      .map(m => ({
        ...m,
        sections: m.sections
          .map(s => ({ ...s, topics: s.topics.filter(matches) }))
          .filter(s => s.topics.length > 0),
      }))
      .filter(m => m.sections.length > 0);
  });

  // ---- Contact form (landing only) -----------------------------------------
  protected readonly contactName = new FormControl<string>('', {
    nonNullable: true,
    validators: [Validators.required, Validators.maxLength(80)],
  });
  protected readonly contactEmail = new FormControl<string>('', {
    nonNullable: true,
    validators: [Validators.required, Validators.email],
  });
  protected readonly contactMessage = new FormControl<string>('', {
    nonNullable: true,
    validators: [Validators.required, Validators.minLength(10), Validators.maxLength(2000)],
  });
  protected readonly contactSubmitted = signal<boolean>(false);
  protected readonly contactSending = signal<boolean>(false);

  constructor() {
    this.searchControl.valueChanges.subscribe(v => this.query.set(v ?? ''));

    // Load the open topic's chunk. A sequence number drops a slow response
    // that lands after the user has already moved to another topic.
    effect(() => {
      const active = this.activeTopic();
      const seq = ++this.loadSeq;
      this.body.set(null);
      if (!active) return;
      active.topic.load()
        .then(body => { if (seq === this.loadSeq) this.body.set(body); })
        .catch(() => {
          if (seq !== this.loadSeq) return;
          this.body.set({
            blocks: [{ kind: 'note', intent: 'warning', text: 'This topic could not be loaded. Refresh the page and try again.' }],
          });
        });
    });
  }

  /** A module's sections are listed in the tree when it is the open module,
   *  or while searching (so every match is visible). */
  protected isExpanded(module: HelpModule): boolean {
    return this.searching() || module.key === this.moduleKey();
  }

  protected topicCount(module: HelpModule): number {
    return module.sections.reduce((n, s) => n + s.topics.length, 0);
  }

  protected clearSearch(): void {
    this.searchControl.setValue('');
  }

  protected nameError(): string | null {
    const c = this.contactName;
    if (!c.touched) return null;
    if (c.hasError('required')) return 'Name is required.';
    if (c.hasError('maxlength')) return 'Name must be 80 characters or fewer.';
    return null;
  }

  protected emailError(): string | null {
    const c = this.contactEmail;
    if (!c.touched) return null;
    if (c.hasError('required')) return 'Email is required.';
    if (c.hasError('email')) return 'Enter a valid email address.';
    return null;
  }

  protected messageError(): string | null {
    const c = this.contactMessage;
    if (!c.touched) return null;
    if (c.hasError('required')) return 'Please describe your question.';
    if (c.hasError('minlength')) return 'Add at least 10 characters of context.';
    if (c.hasError('maxlength')) return 'Message must be 2000 characters or fewer.';
    return null;
  }

  protected submitContact(): void {
    this.contactName.markAsTouched();
    this.contactEmail.markAsTouched();
    this.contactMessage.markAsTouched();
    if (this.contactName.invalid || this.contactEmail.invalid || this.contactMessage.invalid) {
      return;
    }
    // Simulated send — there is no support endpoint yet (spec §3.3).
    this.contactSending.set(true);
    setTimeout(() => {
      this.contactSending.set(false);
      this.contactSubmitted.set(true);
      this.toast.success('Thanks — we\'ll get back to you within one business day.');
      this.contactName.reset('');
      this.contactEmail.reset('');
      this.contactMessage.reset('');
    }, 600);
  }
}
