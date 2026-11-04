import { ViewModel, isRealInstanceId } from '@core/viewmodels/viewmodel';

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const EMPTY_GUID = '00000000-0000-0000-0000-000000000000';

/**
 * The base's whole job is that a row reaching the server always carries a real
 * Guid. `null`, `''` and the empty Guid are the three values that break that —
 * the first fails Newtonsoft deserialization outright, and the other two are
 * accepted and then become the stored row's permanent id.
 */
describe('ViewModel instanceId', () => {
  it('mints an id with no source object', () => {
    expect(new ViewModel().instanceId).toMatch(UUID);
  });

  it('mints an id when the source carries none', () => {
    expect(new ViewModel({ rowVersion: 'v1' }).instanceId).toMatch(UUID);
  });

  it('keeps a server-supplied id', () => {
    expect(new ViewModel({ instanceId: 'server-id' }).instanceId).toBe('server-id');
  });

  for (const [label, value] of [
    ['null', null],
    ['undefined', undefined],
    ['an empty string', ''],
    ['whitespace', '   '],
    ['the empty Guid', EMPTY_GUID],
  ] as [string, string | null | undefined][]) {
    it(`mints an id rather than keeping ${label}`, () => {
      expect(new ViewModel({ instanceId: value }).instanceId).toMatch(UUID);
    });
  }

  it('gives every instance a distinct id', () => {
    expect(new ViewModel().instanceId).not.toBe(new ViewModel().instanceId);
  });
});

describe('isRealInstanceId', () => {
  it('accepts a populated id', () => {
    expect(isRealInstanceId('c0ffee')).toBe(true);
  });

  it('rejects blanks, the empty Guid and non-strings', () => {
    for (const value of [null, undefined, '', '  ', EMPTY_GUID, 0, {}, []]) {
      expect(isRealInstanceId(value)).toBe(false);
    }
  });
});
