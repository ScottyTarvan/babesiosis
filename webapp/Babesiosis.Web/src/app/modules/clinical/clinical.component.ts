import { ChangeDetectionStrategy, Component, computed, DestroyRef, ElementRef, inject, OnInit, signal, viewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { catchError, forkJoin, map, Observable, of, switchMap } from 'rxjs';
import {
  FsBadgeComponent,
  FsBannerComponent,
  FsButtonComponent,
  FsCardComponent,
  FsEmptyStateComponent,
  FsPageHeaderComponent,
  FsSpinnerComponent,
  FsSymbolComponent,
  FsTextInputComponent,
} from '@core';
import { errorMessage } from 'app/core/http-error';
import { ClinicalService } from 'app/modules/clinical/clinical.service';
import { ClinicalTextComponent, clinicalReferenceElementId } from 'app/modules/clinical/clinical-text.component';
import {
  CLINICAL_BASIS_LABELS,
  CLINICAL_CLASS_LABELS,
  CLINICAL_EVIDENCE,
  CLINICAL_STATUS,
  ClinicalIndexGroupViewModel,
  ClinicalIndexPageViewModel,
  ClinicalLegendItem,
  ClinicalPageViewModel,
  ClinicalReferenceViewModel,
  referenceLink,
} from 'app/modules/clinical/viewmodels/clinical.viewmodel';

/** What is known about one page file: read, not written yet, or failed to load. */
interface ClinicalPageState {
  page: ClinicalPageViewModel | null;
  failed: boolean;
}

/**
 * The Clinical screen: a manual for veterinarians, one page for each clinical
 * syndrome of canine babesiosis. The rail on the left lists the pages of
 * `assets/clinical/index.json` under their groups; the selected page is drawn on
 * the right from its page file (`assets/clinical/<ID>.json`), always in the same
 * sections. The selection is the URL (`/clinical/:id`), so a page can be linked to.
 * The format of a page file is in /clinical/content-format.md.
 */
@Component({
  selector: 'fs-clinical',
  standalone: true,
  imports: [
    ClinicalTextComponent,
    FormsModule,
    FsBadgeComponent,
    FsBannerComponent,
    FsButtonComponent,
    FsCardComponent,
    FsEmptyStateComponent,
    FsPageHeaderComponent,
    FsSpinnerComponent,
    FsSymbolComponent,
    FsTextInputComponent,
    RouterLink,
  ],
  templateUrl: './clinical.component.html',
  styleUrls: ['./clinical.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClinicalComponent implements OnInit {
  private readonly clinicalService = inject(ClinicalService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly destroyRef = inject(DestroyRef);

  private readonly detailElement = viewChild<ElementRef<HTMLElement>>('detail');

  protected readonly indexGroups = signal<ClinicalIndexGroupViewModel[]>([]);
  /** Every page file of the index, read once: the rail needs to know which are written. */
  protected readonly pages = signal<Map<string, ClinicalPageState>>(new Map());
  protected readonly loading = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly filter = signal('');
  protected readonly selectedId = signal<string | null>(null);

  protected readonly statusLegend = CLINICAL_STATUS;
  protected readonly evidenceLegend = CLINICAL_EVIDENCE;

  protected readonly allPages = computed<ClinicalIndexPageViewModel[]>(() =>
    this.indexGroups().flatMap(g => g.pages ?? []));
  protected readonly writtenCount = computed(() =>
    this.allPages().filter(p => !!this.pages().get(p.id)?.page).length);

  /** The rail after the filter box. The order is the order of the index. */
  protected readonly groups = computed<ClinicalIndexGroupViewModel[]>(() => {
    const term = this.filter().trim().toLowerCase();
    return this.indexGroups()
      .map(g => ({
        group: g.group,
        pages: (g.pages ?? []).filter(p => !term
          || p.title.toLowerCase().includes(term)
          || p.id.toLowerCase().includes(term)
          || g.group.toLowerCase().includes(term)),
      }))
      .filter(g => g.pages.length > 0);
  });

  protected readonly selectedEntry = computed(() =>
    this.allPages().find(p => p.id === this.selectedId()) ?? null);
  protected readonly selectedState = computed(() => {
    const id = this.selectedId();
    return id ? this.pages().get(id) ?? null : null;
  });
  protected readonly page = computed(() => this.selectedState()?.page ?? null);

  /** The Babesia species named in the species notes, shown in the header. */
  protected readonly species = computed(() =>
    (this.page()?.species_notes ?? []).map(n => n.species).filter(s => !!s));
  /** The reference list in the order of its keys (R1, R2, ...). */
  protected readonly references = computed<ClinicalReferenceViewModel[]>(() =>
    [...(this.page()?.references ?? [])].sort((a, b) => this.refNumber(a.ref) - this.refNumber(b.ref)));

  ngOnInit(): void {
    // The route is the selection. The matcher reuses this component across pages.
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(params => {
        this.selectedId.set(params.get('id'));
        this.selectFirst();
      });

    this.load();
  }

  /** Reads the index, then every page file of it. A page that is missing is not an error. */
  protected load(): void {
    this.loading.set(true);
    this.error.set(null);
    this.clinicalService.getIndex().pipe(
      switchMap(index => {
        const groups = index?.groups ?? [];
        const ids = groups.flatMap(g => g.pages ?? []).map(p => p.id);
        const requests: Observable<[string, ClinicalPageState]>[] = ids.map(id =>
          this.clinicalService.getPage(id).pipe(
            map(page => [id, { page, failed: false }] as [string, ClinicalPageState]),
            catchError(() => of([id, { page: null, failed: true }] as [string, ClinicalPageState])),
          ));
        return (requests.length ? forkJoin(requests) : of([])).pipe(map(states => ({ groups, states })));
      }),
      takeUntilDestroyed(this.destroyRef),
    ).subscribe({
      next: ({ groups, states }) => {
        this.indexGroups.set(groups);
        this.pages.set(new Map(states));
        this.loading.set(false);
        this.selectFirst();
      },
      error: err => {
        this.loading.set(false);
        this.error.set(errorMessage(err, 'The clinical manual could not be loaded.'));
      },
    });
  }

  protected select(id: string): void {
    if (id !== this.selectedId()) {
      this.router.navigate(['/clinical', id]).then(() =>
        this.detailElement()?.nativeElement.scrollIntoView({ block: 'start' }));
    }
  }

  protected print(): void {
    window.print();
  }

  protected isWritten(id: string): boolean {
    return !!this.pages().get(id)?.page;
  }

  protected pageTitle(id: string): string {
    return this.allPages().find(p => p.id === id)?.title ?? id;
  }

  protected status(key: string | undefined): ClinicalLegendItem {
    return this.statusLegend.find(s => s.key === key)
      ?? { key: key ?? '', label: key || 'Status not given', intent: 'secondary', meaning: '' };
  }

  protected evidence(key: string | undefined): ClinicalLegendItem {
    return this.evidenceLegend.find(e => e.key === key)
      ?? { key: key ?? '', label: key ? `Level ${key}` : 'Level not given', intent: 'secondary', meaning: '' };
  }

  protected classLabel(key: string | undefined): string {
    return key ? CLINICAL_CLASS_LABELS[key] ?? key : '';
  }

  protected basisLabel(key: string | undefined): string {
    return key ? CLINICAL_BASIS_LABELS[key] ?? key : '';
  }

  protected link(ref: ClinicalReferenceViewModel): string | null {
    return referenceLink(ref);
  }

  protected linkLabel(ref: ClinicalReferenceViewModel): string {
    if ((ref.doi ?? '').trim()) return 'DOI';
    if ((ref.pmid ?? '').trim()) return 'PubMed';
    return 'Source';
  }

  protected refNumber(ref: string): number {
    return Number(ref.replace(/^R/, '')) || 0;
  }

  protected refElementId(ref: string): string {
    return clinicalReferenceElementId(ref);
  }

  /** `/clinical` opens the first page of the index. */
  private selectFirst(): void {
    const first = this.allPages()[0];
    if (!this.selectedId() && first) {
      this.router.navigate(['/clinical', first.id], { replaceUrl: true });
    }
  }
}
