using System;

namespace Babesiosis.Core.Exceptions
{
  /// <summary>
  /// A business rule the caller broke, carrying a message written to be shown to them —
  /// "'Warehouse SQL' can't be deleted — 2 datasets (Country, Currency) are still attached to it".
  ///
  /// <para>
  /// Every <see cref="Assertions.Assertion"/> helper that expresses a rule throws this. It exists
  /// so the HTTP layer can tell a rule violation apart from a genuine fault: the first is the
  /// user's to fix and its message is safe and useful to return, while the second is a bug whose
  /// message ("Sequence contains no elements") means nothing to them and may leak internals. The
  /// former answers 400 with the real text; the latter stays a 500 behind a generic message.
  /// </para>
  ///
  /// <para>
  /// Derives from <see cref="InvalidOperationException"/> — the type these assertions threw
  /// before — so any caller still catching that keeps working.
  /// </para>
  /// </summary>
  public class ValidationException : InvalidOperationException
  {
    public ValidationException(string message) : base(message)
    {
    }
  }
}
