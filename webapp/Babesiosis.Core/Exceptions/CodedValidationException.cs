using System;

namespace Babesiosis.Core.Exceptions
{
  /// <summary>
  /// A <see cref="ValidationException"/> that also carries a machine-readable <see cref="Code"/>
  /// the SPA can branch on, an optional structured <see cref="Errors"/> payload (e.g. the offending
  /// field names for <c>REQUIRED_FIELDS_UNBOUND</c>), and a <see cref="StatusCode"/> for the rare
  /// case where 422 is not the right answer — <c>SOURCE_FILE_TOO_LARGE</c> wants 413.
  ///
  /// <para>
  /// Everything <see cref="ValidationException"/> says about a rule violation being the caller's to
  /// fix, safe to surface as-is, still applies here — this only adds the extra fields the mappings
  /// feature's error envelope needs (source-to-dataset-mapping-brief.md §4) without touching the
  /// plain-<see cref="ValidationException"/> path any existing caller already relies on.
  /// </para>
  /// </summary>
  public class CodedValidationException : ValidationException
  {
    public string Code { get; }

    public int StatusCode { get; }

    public object Errors { get; }

    public CodedValidationException(string code, string message)
      : this(code, message, errors: null, statusCode: 422)
    {
    }

    public CodedValidationException(string code, string message, int statusCode)
      : this(code, message, errors: null, statusCode: statusCode)
    {
    }

    public CodedValidationException(string code, string message, object errors)
      : this(code, message, errors, statusCode: 422)
    {
    }

    public CodedValidationException(string code, string message, object errors, int statusCode)
      : base(message)
    {
      Code = code;
      Errors = errors;
      StatusCode = statusCode;
    }
  }
}
