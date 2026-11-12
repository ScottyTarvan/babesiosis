import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import { splitCitations } from 'app/modules/clinical/viewmodels/clinical.viewmodel';

/** The DOM id of a reference list entry; the Clinical page gives each entry this id. */
export function clinicalReferenceElementId(ref: string): string {
  return `clinical-ref-${ref}`;
}

/**
 * A text field of a page file, with its citation markers (`[R1]`) as links to the
 * reference list. With `refs`, it shows a list of reference keys the same way.
 * The text is bound as text: a page file can never put markup on the screen.
 */
@Component({
  selector: 'fs-clinical-text',
  standalone: true,
  templateUrl: './clinical-text.component.html',
  styleUrls: ['./clinical-text.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ClinicalTextComponent {
  readonly text = input<string | null | undefined>('');
  readonly refs = input<string[] | null | undefined>(null);

  protected readonly parts = computed(() => splitCitations(this.text()));
  protected readonly keys = computed(() =>
    (this.refs() ?? []).map(ref => ({ ref, label: ref.replace(/^R/, '') })));

  /** Scroll to the entry and focus it, so the reader sees which one was meant. */
  protected open(ref: string): void {
    const entry = document.getElementById(clinicalReferenceElementId(ref));
    if (entry) {
      // Focus first: a focus call after scrollIntoView stops a smooth scroll.
      entry.focus({ preventScroll: true });
      entry.scrollIntoView({ block: 'center' });
    }
  }
}
