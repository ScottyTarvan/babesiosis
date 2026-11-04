namespace Babesiosis.Core.Exceptions
{
  /// <summary>
  /// The machine-readable codes the Data Lineage › Diagrams feature can raise (diagrams.md §3.11), all
  /// answered as HTTP 422 through <see cref="CodedValidationException"/>. Held as consts for the same
  /// reason <see cref="MappingErrorCodes"/> is: the SPA's branching has one spelling to trust.
  /// <para>
  /// A diagram id that does not exist in the caller's Environment has NO code of its own — it is a
  /// plain <see cref="ValidationException"/> (diagrams.md §3.2).
  /// </para>
  /// </summary>
  public static class MappingDiagramErrorCodes
  {
    /// <summary>The diagram name is already used in this Environment. The clashing name is in <c>errors</c>.</summary>
    public const string DIAGRAM_NAME_DUPLICATE = "DIAGRAM_NAME_DUPLICATE";

    /// <summary>
    /// A mapping in the selection does not exist in the diagram's Environment. The missing mapping
    /// ids are in <c>errors</c>.
    /// </summary>
    public const string DIAGRAM_MAPPING_NOT_FOUND = "DIAGRAM_MAPPING_NOT_FOUND";

    /// <summary>The layout is not a JSON object, or is 1,000,000 characters or longer.</summary>
    public const string DIAGRAM_LAYOUT_INVALID = "DIAGRAM_LAYOUT_INVALID";
  }
}
