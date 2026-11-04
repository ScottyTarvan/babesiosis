using Babesiosis.Core.Exceptions;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// A source file the parser refused, carrying the machine-readable code the PRD §5 error envelope
  /// has to surface — <c>PARSE_FAILED</c>, <c>UNSUPPORTED_FILE_TYPE</c> or
  /// <c>INVALID_FIXED_WIDTH_LAYOUT</c>.
  ///
  /// <para>
  /// It lives in <c>Babesiosis.Core</c> and knows nothing about HTTP: the code is a plain string,
  /// not a status. The Functions layer owns the code → status mapping (all three are 422). Making
  /// this type depend on the Functions layer would invert the dependency direction the architecture
  /// docs fix, and would stop the parser being testable on its own.
  /// </para>
  ///
  /// <para>
  /// Derives from <see cref="ValidationException"/> deliberately. These are always the caller's file
  /// or the caller's parse options at fault, never a bug, so the message is safe to show them; and
  /// if a controller ever forgets to translate the code, the existing
  /// <see cref="ValidationException"/> catch still answers 400 with real text rather than a generic
  /// 500. The coded catch must be registered ahead of it to get the code out.
  /// </para>
  /// </summary>
  public class SourceParseException : ValidationException
  {
    /// <summary>The file could not be read as the declared format.</summary>
    public const string ParseFailedCode = "PARSE_FAILED";

    /// <summary>The declared format is not one this module can parse.</summary>
    public const string UnsupportedFileTypeCode = "UNSUPPORTED_FILE_TYPE";

    /// <summary>The fixed-width layout is self-contradictory — overlapping or non-positive.</summary>
    public const string InvalidFixedWidthLayoutCode = "INVALID_FIXED_WIDTH_LAYOUT";

    public SourceParseException(string code, string message, int? lineNumber = null)
      : base(message)
    {
      Code = code;
      LineNumber = lineNumber;
    }

    /// <summary>
    /// The PRD §5 error code. Never null — every construction path goes through one of the three
    /// factories below.
    /// </summary>
    public string Code { get; }

    /// <summary>
    /// The 1-based line (delimited / fixed width) or row (Excel) the parse gave up on, when the
    /// failure can be pinned to one. PRD §6 requires it on <c>PARSE_FAILED</c>: "on failure return
    /// PARSE_FAILED with the failing row/line number". Null for whole-file failures — an empty file
    /// or an unreadable workbook has no failing line.
    /// </summary>
    public int? LineNumber { get; }

    /// <summary>The declared format could not read the bytes. <paramref name="lineNumber"/> is 1-based.</summary>
    public static SourceParseException ParseFailed(string message, int? lineNumber = null)
    {
      return new SourceParseException(ParseFailedCode, message, lineNumber);
    }

    /// <summary>No parser exists for the requested format.</summary>
    public static SourceParseException UnsupportedFileType(string message)
    {
      return new SourceParseException(UnsupportedFileTypeCode, message);
    }

    /// <summary>The fixed-width layout was rejected before a single byte of the file was read.</summary>
    public static SourceParseException InvalidFixedWidthLayout(string message)
    {
      return new SourceParseException(InvalidFixedWidthLayoutCode, message);
    }
  }
}
