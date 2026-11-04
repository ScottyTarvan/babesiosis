import { errorCode } from 'app/core/http-error';

/**
 * errorCode only — errorMessage predates this file and its behaviour is untouched, so it is
 * not re-covered here. See CodedValidationException / MappingErrorCodes (Babesiosis.Core)
 * for where `code` on the envelope comes from.
 */
describe('errorCode', () => {
  it('reads code off the same { error: {...} } envelope errorMessage reads', () => {
    const err = { error: { code: 'DATASET_NOT_DEPLOYED', message: 'Not deployed' } };
    expect(errorCode(err)).toBe('DATASET_NOT_DEPLOYED');
  });

  it('returns null when the body is a bare string (the ConcurrencyException 409 shape)', () => {
    const err = { error: 'Someone else already saved this record' };
    expect(errorCode(err)).toBeNull();
  });

  it('returns null when err itself is a bare string', () => {
    expect(errorCode('Some raw error text')).toBeNull();
  });

  it('returns null when the envelope has no code key (a plain ValidationException 400 body)', () => {
    const err = { error: { message: 'A rule was broken' } };
    expect(errorCode(err)).toBeNull();
  });

  it('returns null when code is present but blank', () => {
    const err = { error: { code: '   ' } };
    expect(errorCode(err)).toBeNull();
  });

  it('returns null when there is no error property at all', () => {
    expect(errorCode({ message: 'network down' })).toBeNull();
  });

  it('returns null for null/undefined input', () => {
    expect(errorCode(null)).toBeNull();
    expect(errorCode(undefined)).toBeNull();
  });
});
