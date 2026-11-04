namespace Babesiosis.Core.Exceptions
{
  /// <summary>
  /// The machine-readable codes the Source-to-DataSet Mappings feature can raise. Held as consts so
  /// a call site throwing <see cref="CodedValidationException"/> references
  /// <c>MappingErrorCodes.DATASET_NOT_DEPLOYED</c> rather than a bare string, and the SPA's branching
  /// in http-error.ts has one spelling to trust.
  /// </summary>
  public static class MappingErrorCodes
  {
    public const string DATASET_NOT_DEPLOYED = "DATASET_NOT_DEPLOYED";
    public const string MAPPING_NAME_DUPLICATE = "MAPPING_NAME_DUPLICATE";
    public const string SOURCE_FILE_TOO_LARGE = "SOURCE_FILE_TOO_LARGE";
    public const string UNSUPPORTED_FILE_TYPE = "UNSUPPORTED_FILE_TYPE";
    public const string PARSE_FAILED = "PARSE_FAILED";
    public const string INVALID_FIXED_WIDTH_LAYOUT = "INVALID_FIXED_WIDTH_LAYOUT";

    /// <summary>
    /// A cell save picked a target field another source field in the same dataset already feeds.
    /// The offending target field names are in the envelope's <c>errors</c>.
    /// </summary>
    public const string TARGET_FIELD_ALREADY_BOUND = "TARGET_FIELD_ALREADY_BOUND";

    /// <summary>A source field name is already used on this mapping (case-insensitive).</summary>
    public const string SOURCE_FIELD_NAME_DUPLICATE = "SOURCE_FIELD_NAME_DUPLICATE";

    /// <summary>
    /// A source upload's removals no longer match the ones confirmed on its preview — the mapping
    /// moved in between. Nothing was written; the screen re-previews and asks again.
    /// </summary>
    public const string SOURCE_PREVIEW_STALE = "SOURCE_PREVIEW_STALE";

    /// <summary>
    /// A header save (add, edit, a Source Type change) or an Add DataSets on a mapping with no
    /// linked service. Field-level against Linked Service.
    /// </summary>
    public const string MAPPING_LINKED_SERVICE_REQUIRED = "MAPPING_LINKED_SERVICE_REQUIRED";

    /// <summary>
    /// The linked service is in another environment, does not exist, or is not of type SQL.
    /// Field-level against Linked Service.
    /// </summary>
    public const string MAPPING_LINKED_SERVICE_INVALID = "MAPPING_LINKED_SERVICE_INVALID";

    /// <summary>
    /// Edit changed the linked service while a target dataset belongs to a different one. The
    /// offending dataset names are in the envelope's <c>errors</c>. Field-level against Linked Service.
    /// </summary>
    public const string MAPPING_LINKED_SERVICE_IN_USE = "MAPPING_LINKED_SERVICE_IN_USE";

    /// <summary>
    /// A dataset being added belongs to a linked service other than the mapping's. The offending
    /// dataset names are in the envelope's <c>errors</c>.
    /// </summary>
    public const string MAPPING_DATASET_WRONG_LINKED_SERVICE = "MAPPING_DATASET_WRONG_LINKED_SERVICE";

    /// <summary>
    /// A source upload, preview or options-only edit named a format that does not belong to the
    /// mapping's Source Type: Excel needs Source Type Excel; Delimited and Fixed Width need File.
    /// Refused before any parse or write. The format's name is in the envelope's <c>errors</c>.
    /// Field-level against the format.
    /// </summary>
    public const string SOURCE_FORMAT_MISMATCH = "SOURCE_FORMAT_MISMATCH";
  }
}
