import { MockRegistration } from 'app/_mocks/mock-handler';
import { GetArticleListCommand } from 'app/modules/reference-articles/commands/get-article-list.command';
import { ArticleListViewModel, ArticleViewModel } from 'app/modules/reference-articles/viewmodels/article.viewmodel';

/**
 * Mirrors `GetArticleListController`: filters, sorts on one column (newest
 * first by default) and pages by skip/take. Rows are illustrative, not real
 * articles.
 */
const articles: ArticleViewModel[] = [
  {
    id: 1, code: 'CB901', pubDate: '2023-04-12', pubDatePrecision: 'D', categoryName: 'Renal injury and renal function',
    categoryCode: 'REN', categoryLabel: 'Kidney', studyType: 'Associational', species: 'B. rossi', country: 'South Africa', journal: 'Veterinary Parasitology',
    title: 'Acute kidney injury in dogs naturally infected with Babesia rossi',
    summary: 'Azotaemia at admission was associated with higher mortality in dogs with B. rossi infection.',
    doi: '10.1000/example.2023.001', pmid: '30000001', sourceUrl: 'https://doi.org/10.1000/example.2023.001',
  },
  {
    id: 2, code: 'CB902', pubDate: '2021-09-01', pubDatePrecision: 'M', categoryName: 'Erythrocyte injury, haemolysis, anaemia and immune-mediated processes',
    categoryCode: 'ERY', categoryLabel: 'Red cells and anaemia', studyType: 'Descriptive', species: 'B. canis', country: 'Poland', journal: 'Parasites & Vectors',
    title: 'Haematological changes in canine babesiosis caused by Babesia canis',
    summary: 'Thrombocytopenia was the most consistent haematological finding across all severity grades.',
    doi: null, pmid: '30000002', sourceUrl: 'https://pubmed.ncbi.nlm.nih.gov/30000002/',
  },
  {
    id: 3, code: 'CB903', pubDate: '2019-01-01', pubDatePrecision: 'Y', categoryName: null, categoryCode: null, categoryLabel: null,
    studyType: 'Descriptive', species: 'Not identified in text read', country: null, journal: 'Journal of the South African Veterinary Association',
    title: 'A retrospective review of canine babesiosis cases at a referral hospital',
    summary: 'Most cases presented in summer, with young dogs over-represented.',
    doi: null, pmid: null, sourceUrl: null,
  },
];

/**
 * The server's filter grammar, in small: `[field, op, value]` conditions joined
 * by "and" / "or" ("and" binds tighter), text operators case-insensitive.
 * Calendar dates compare as their yyyy-MM-dd text.
 */
function matches(row: ArticleViewModel, filter: unknown): boolean {
  if (!Array.isArray(filter) || filter.length === 0) return true;
  if (typeof filter[0] === 'string') return condition(row, filter as [keyof ArticleViewModel, string, unknown]);

  const orTerms: boolean[] = [];
  let andChain = true;
  for (const part of filter) {
    if (part === 'or') {
      orTerms.push(andChain);
      andChain = true;
    } else if (part !== 'and') {
      andChain = andChain && matches(row, part);
    }
  }
  orTerms.push(andChain);
  return orTerms.some(Boolean);
}

function condition(row: ArticleViewModel, [field, op, value]: [keyof ArticleViewModel, string, unknown]): boolean {
  const cell = String(row[field] ?? '').toLowerCase();
  const target = String(value ?? '').toLowerCase();
  switch (op) {
    case 'contains': return cell.includes(target);
    case 'notcontains': return !cell.includes(target);
    case 'startswith': return cell.startsWith(target);
    case 'endswith': return cell.endsWith(target);
    case '=': return cell === target;
    case '<>': return cell !== target;
    case '<': return cell < target;
    case '>': return cell > target;
    case '<=': return cell <= target;
    case '>=': return cell >= target;
    default: return true;
  }
}

export const articlesListGetMock: MockRegistration<GetArticleListCommand, ArticleListViewModel> = {
  route: 'articles-list-get',
  handler: command => {
    const options = command?.loadOptions ?? {};
    const skip = options.skip ?? 0;
    const take = options.take || 500;
    const [sort] = (options.sort as { selector: keyof ArticleViewModel; desc: boolean }[] | undefined)
      ?? [{ selector: 'pubDate', desc: true }];

    const sorted = articles.filter(row => matches(row, options.filter)).sort((a, b) => {
      const order = String(a[sort.selector] ?? '').localeCompare(String(b[sort.selector] ?? ''));
      return sort.desc ? -order : order;
    });
    const items = sorted.slice(skip, skip + take);
    const totalPages = Math.ceil(sorted.length / take);
    const pageIndex = Math.floor(skip / take);

    return {
      page: {
        items,
        paging: {
          totalCount: sorted.length,
          pageIndex,
          pageSize: take,
          totalPages,
          hasPreviousPage: pageIndex > 0,
          hasNextPage: pageIndex + 1 < totalPages,
        },
      },
      permissions: {},
    };
  },
};
