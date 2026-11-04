import { FsPageState, FsSortState, FsTableColumn } from '@fundstream-ai/gnome-ui';
import { buildLoadOptions } from 'app/core/utils/load-options';

interface Row {
  name: string;
  status: number;
  isAdmin: boolean;
  createdDate: string;
  clientName: string;
}

const columns: FsTableColumn<Row>[] = [
  { key: 'name', label: 'Name', filter: { type: 'search' } },
  {
    key: 'status',
    label: 'Status',
    filter: { type: 'multi-select', options: [{ value: 0, label: 'A' }, { value: 1, label: 'B' }] },
  },
  {
    key: 'isAdmin',
    label: 'Admin',
    filter: { type: 'single-select', options: [{ value: true, label: 'Yes' }, { value: false, label: 'No' }] },
  },
  { key: 'createdDate', label: 'Created', filter: { type: 'date-range' } },
  { key: 'clientName', label: 'Client', filter: { type: 'search' } },
];

const page: FsPageState = { pageIndex: 2, pageSize: 25 };
const sort: FsSortState = { key: 'name', direction: 'desc' };

describe('buildLoadOptions', () => {
  it('maps page to skip/take and always requests the total count', () => {
    const result = buildLoadOptions({}, null, page, { columns });
    expect(result.skip).toBe(50);
    expect(result.take).toBe(25);
    expect(result.requireTotalCount).toBeTrue();
  });

  it('maps sort to a selector/desc descriptor', () => {
    const result = buildLoadOptions({}, sort, page, { columns });
    expect(result.sort).toEqual([{ selector: 'name', desc: true }]);
  });

  it('omits filter when no column filters are active', () => {
    const result = buildLoadOptions({ name: '   ' }, null, page, { columns });
    expect(result.filter).toBeUndefined();
  });

  it('builds a contains clause for a search filter', () => {
    const result = buildLoadOptions({ name: 'ac' }, null, page, { columns });
    expect(result.filter).toEqual(['name', 'contains', 'ac']);
  });

  it('builds an equals clause for a single-select filter', () => {
    const result = buildLoadOptions({ isAdmin: true }, null, page, { columns });
    expect(result.filter).toEqual(['isAdmin', '=', true]);
  });

  it('collapses a single multi-select value to one equals clause', () => {
    const result = buildLoadOptions({ status: [1] }, null, page, { columns });
    expect(result.filter).toEqual(['status', '=', 1]);
  });

  it('joins multiple multi-select values with "or"', () => {
    const result = buildLoadOptions({ status: [0, 1] }, null, page, { columns });
    expect(result.filter).toEqual([['status', '=', 0], 'or', ['status', '=', 1]]);
  });

  it('builds an inclusive end-of-day range for a date-range filter', () => {
    const result = buildLoadOptions(
      { createdDate: { from: '2026-01-01', to: '2026-01-31' } }, null, page, { columns });
    const filter = result.filter as unknown[];
    expect(filter[0]).toEqual(['createdDate', '>=', '2026-01-01']);
    expect(filter[1]).toBe('and');
    const upper = filter[2] as unknown[];
    expect(upper[0]).toBe('createdDate');
    expect(upper[1]).toBe('<=');
    expect(new Date(upper[2] as string).getHours() >= 0).toBeTrue();
  });

  it('combines multiple active filters with "and"', () => {
    const result = buildLoadOptions({ name: 'ac', isAdmin: false }, null, page, { columns });
    expect(result.filter).toEqual([['name', 'contains', 'ac'], 'and', ['isAdmin', '=', false]]);
  });

  it('applies a selector map to filter and sort keys', () => {
    const result = buildLoadOptions(
      { clientName: 'ac' },
      { key: 'clientName', direction: 'asc' },
      page,
      { columns, selectorMap: { clientName: 'Client.Name' } },
    );
    expect(result.filter).toEqual(['Client.Name', 'contains', 'ac']);
    expect(result.sort).toEqual([{ selector: 'Client.Name', desc: false }]);
  });
});
