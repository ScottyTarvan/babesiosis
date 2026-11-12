// The shapes of the static files of the clinical manual. The field names are those of the
// files (snake_case), so a page file is used as it is read. The format is defined in
// /clinical/content-format.md; the files are in public/assets/clinical/.

/** One link of the rail: `assets/clinical/index.json`. */
export interface ClinicalIndexPageViewModel {
  id: string;
  title: string;
}

export interface ClinicalIndexGroupViewModel {
  group: string;
  pages: ClinicalIndexPageViewModel[];
}

export interface ClinicalIndexViewModel {
  groups: ClinicalIndexGroupViewModel[];
}

export interface ClinicalSectionViewModel {
  heading: string;
  text: string;
}

export interface ClinicalSpeciesNoteViewModel {
  species: string;
  note: string;
}

export interface ClinicalCriterionViewModel {
  criterion: string;
  threshold: string;
  /** babesiosis, general canine, human, working. */
  basis: string;
  note?: string;
  refs?: string[];
}

export interface ClinicalSignViewModel {
  sign: string;
  note?: string;
  refs?: string[];
}

export interface ClinicalTestViewModel {
  test: string;
  finding?: string;
  note?: string;
  refs?: string[];
}

export interface ClinicalDifferentialViewModel {
  condition: string;
  distinguish?: string;
  refs?: string[];
}

export interface ClinicalGradeViewModel {
  grade: string;
  criteria?: string;
  refs?: string[];
}

export interface ClinicalDiagnosisViewModel {
  criteria?: ClinicalCriterionViewModel[];
  clinical_signs?: ClinicalSignViewModel[];
  tests?: ClinicalTestViewModel[];
  differentials?: ClinicalDifferentialViewModel[];
  grading?: ClinicalGradeViewModel[];
}

export interface ClinicalApproachStepViewModel {
  step?: number;
  action: string;
  detail?: string;
  /** practice or referral. */
  setting?: string;
}

export interface ClinicalDoseViewModel {
  drug: string;
  dose: string;
  route?: string;
  frequency?: string;
  duration?: string;
  context?: string;
  note?: string;
  refs?: string[];
}

export interface ClinicalTreatmentViewModel {
  name: string;
  /** antibabesial, specific, supportive, adjunct. */
  class?: string;
  aim?: string;
  /** standard, proposed, conflicting, no_benefit, harmful. */
  status?: string;
  /** A to E. */
  evidence_level?: string;
  independent_studies?: number;
  evidence_summary?: string;
  doses?: ClinicalDoseViewModel[];
  cautions?: string;
  monitoring?: string;
  availability?: string;
  refs?: string[];
}

export interface ClinicalIndicatorViewModel {
  finding: string;
  meaning?: string;
  refs?: string[];
}

export interface ClinicalPrognosisViewModel {
  text?: string;
  indicators?: ClinicalIndicatorViewModel[];
}

export interface ClinicalRelatedViewModel {
  id: string;
  why?: string;
}

export interface ClinicalReferenceViewModel {
  /** R1, R2, ... */
  ref: string;
  authors?: string;
  year?: number | string;
  title?: string;
  journal?: string;
  volume_pages?: string;
  doi?: string;
  pmid?: string;
  url?: string;
  /** The local article ID (CB050) when the paper is in the review. */
  article_id?: string;
  type?: string;
  species?: string;
  n_dogs?: number | null;
  /** full text or abstract: what the agent read. */
  read?: string;
}

export interface ClinicalSearchViewModel {
  date?: string;
  sources?: string[];
  note?: string;
}

/** One page of the manual: `assets/clinical/<ID>.json`. */
export interface ClinicalPageViewModel {
  schema_version: number;
  id: string;
  title: string;
  updated?: string;
  definition?: string;
  definition_note?: string;
  key_points?: string[];
  description?: ClinicalSectionViewModel[];
  species_notes?: ClinicalSpeciesNoteViewModel[];
  diagnosis?: ClinicalDiagnosisViewModel;
  approach?: ClinicalApproachStepViewModel[];
  treatments?: ClinicalTreatmentViewModel[];
  prognosis?: ClinicalPrognosisViewModel;
  related?: ClinicalRelatedViewModel[];
  evidence_gaps?: string[];
  references?: ClinicalReferenceViewModel[];
  search?: ClinicalSearchViewModel;
}

// ---- Labels and legend (the meanings are those of /clinical/rules.md) ---------------------

export type ClinicalBadgeIntent = 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'info';

export interface ClinicalLegendItem {
  key: string;
  label: string;
  meaning: string;
  intent: ClinicalBadgeIntent;
}

export const CLINICAL_STATUS: ClinicalLegendItem[] = [
  { key: 'standard', label: 'Standard', intent: 'success', meaning: 'Accepted practice for this problem in the sources.' },
  { key: 'proposed', label: 'Proposed', intent: 'info', meaning: 'Suggested or used in some dogs; not established.' },
  { key: 'conflicting', label: 'Conflicting', intent: 'warning', meaning: 'Studies disagree on benefit.' },
  { key: 'no_benefit', label: 'No benefit shown', intent: 'secondary', meaning: 'Studied, and no benefit was found.' },
  { key: 'harmful', label: 'Harmful', intent: 'danger', meaning: 'Reported to cause harm, or contraindicated.' },
];

export const CLINICAL_EVIDENCE: ClinicalLegendItem[] = [
  { key: 'A', label: 'Level A', intent: 'primary', meaning: 'A controlled trial in dogs with babesiosis.' },
  { key: 'B', label: 'Level B', intent: 'primary', meaning: 'A cohort or a case series of five or more dogs with babesiosis.' },
  { key: 'C', label: 'Level C', intent: 'secondary', meaning: 'Case reports, or fewer than five dogs with babesiosis.' },
  { key: 'D', label: 'Level D', intent: 'secondary', meaning: 'Extrapolated from the same syndrome of another cause in dogs, or from humans.' },
  { key: 'E', label: 'Level E', intent: 'secondary', meaning: 'Expert opinion, a textbook or a product label.' },
];

export const CLINICAL_CLASS_LABELS: Record<string, string> = {
  antibabesial: 'Antibabesial',
  specific: 'Specific',
  supportive: 'Supportive',
  adjunct: 'Adjunct',
};

export const CLINICAL_BASIS_LABELS: Record<string, string> = {
  babesiosis: 'Used in babesiosis',
  'general canine': 'General canine',
  human: 'Human',
  working: 'Working threshold',
};

/** The link of a reference: the DOI, else PubMed, else its URL (https only). */
export function referenceLink(ref: ClinicalReferenceViewModel): string | null {
  const doi = (ref.doi ?? '').trim();
  if (doi) return `https://doi.org/${encodeURI(doi)}`;
  const pmid = (ref.pmid ?? '').trim();
  if (/^\d+$/.test(pmid)) return `https://pubmed.ncbi.nlm.nih.gov/${pmid}/`;
  const url = (ref.url ?? '').trim();
  return url.startsWith('https://') ? url : null;
}

/** A piece of a text field: plain text, or a citation marker `[R1]`. */
export interface ClinicalTextPart {
  text: string;
  /** The reference key when the piece is a citation. */
  ref: string | null;
}

/** Splits a text field at its citation markers. `a [R1][R2] b` gives four pieces. */
export function splitCitations(text: string | null | undefined): ClinicalTextPart[] {
  const parts: ClinicalTextPart[] = [];
  const source = text ?? '';
  const marker = /\[(R\d+)\]/g;
  let last = 0;
  let match: RegExpExecArray | null;
  while ((match = marker.exec(source)) !== null) {
    if (match.index > last) {
      parts.push({ text: source.slice(last, match.index), ref: null });
    }
    parts.push({ text: match[1].slice(1), ref: match[1] });
    last = marker.lastIndex;
  }
  if (last < source.length) {
    parts.push({ text: source.slice(last), ref: null });
  }
  return parts;
}
