namespace Babesiosis.Core.Api.Review.Commands
{
  /// <summary>
  /// Loads the article counts per clinical syndrome or sign (curated UMLS terms) for the
  /// Review dashboard's "Clinical syndromes and signs" card. Carries only the number of
  /// terms for now; filters arrive with the dashboard's filter bar.
  /// </summary>
  public class GetTermCountsCommand
  {
    /// <summary>How many terms to return, highest article count first. Default 20.</summary>
    public int Top { get; set; } = 20;
  }
}
