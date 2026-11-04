using System.Text.Json;

namespace Babesiosis.Console.Source
{
  /// <summary>
  /// One line of articles.jsonl. Property names map to the snake_case keys in the file.
  /// Lists that are stored as JSON columns are kept as raw <see cref="JsonElement"/> values.
  /// </summary>
  internal sealed class ArticleRecord
  {
    public string Id { get; set; } = "";
    public string Key { get; set; } = "";
    public string Filename { get; set; } = "";
    public string? ScopeLabel { get; set; }
    public string? IncludeType { get; set; }
    public string Title { get; set; } = "";
    public List<string>? Authors { get; set; }
    public string? Journal { get; set; }
    public string? VolumeIssuePages { get; set; }
    public string? FirstPubDate { get; set; }
    public string? OnlineDate { get; set; }
    public string? IssueDate { get; set; }
    public string? DateNote { get; set; }
    public string? Doi { get; set; }
    public string? Pmid { get; set; }
    public string? Pmcid { get; set; }
    public string? Language { get; set; }
    public string? Corrections { get; set; }
    public JsonElement Species { get; set; }
    public string? SpeciesShort { get; set; }
    public string? Host { get; set; }
    public string? Country { get; set; }
    public string? Design { get; set; }
    public string? SampleSize { get; set; }
    public int? NInfectedDogs { get; set; }
    public int? NControls { get; set; }
    public string? CohortId { get; set; }
    public string? PrimaryCategory { get; set; }
    public List<string>? SecondaryTags { get; set; }
    public string? EvidenceType { get; set; }
    public string? OneSentenceFinding { get; set; }
    public bool? AbstractAvailable { get; set; }
    public string? AbstractSource { get; set; }
    public bool? FulltextChecked { get; set; }
    public string? FulltextUrl { get; set; }
    public bool? SupplementChecked { get; set; }
    public bool? RepositoryChecked { get; set; }
    public string? DataAvailabilityStatement { get; set; }
    public JsonElement DatasetIds { get; set; }
    public int? DatasetStatusCode { get; set; }
    public string? DatasetStatus { get; set; }
    public JsonElement SourceLinks { get; set; }
    public string? AccessDate { get; set; }
    public string? VerificationNotes { get; set; }
    public string? StudyType { get; set; }
    public List<string>? ComparatorCategories { get; set; }
    public bool? OlderFoundational { get; set; }

    public static readonly JsonSerializerOptions JsonOptions = new()
    {
      PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
    };

    /// <summary>Raw JSON text of an element, or null when it is missing or JSON null.</summary>
    public static string? RawJson(JsonElement element) =>
      element.ValueKind is JsonValueKind.Undefined or JsonValueKind.Null ? null : element.GetRawText();
  }
}
