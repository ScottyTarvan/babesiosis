using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>
  /// Article counts per curated term, split into articles that studied the term and
  /// articles that only mentioned it. Canine (CB) articles only.
  /// </summary>
  public class TermCountsViewModel
  {
    /// <summary>CB articles with at least one term row.</summary>
    public int ArticleCount { get; set; }
    /// <summary>CB articles whose terms come from the abstract alone (text_source = abstract).</summary>
    public int AbstractOnlyCount { get; set; }
    /// <summary>The top terms by total article count, highest first.</summary>
    public List<TermCountsRowViewModel> Terms { get; set; } = new List<TermCountsRowViewModel>();
  }

  /// <summary>One term: display name (merged CUIs count once) and its article counts.</summary>
  public class TermCountsRowViewModel
  {
    public string Name { get; set; }
    /// <summary>Articles with an affirmed mention in the title, results, case or conclusion (abstract for abstract-only articles).</summary>
    public int Studied { get; set; }
    /// <summary>Articles that mention the term elsewhere only.</summary>
    public int MentionedOnly { get; set; }
    /// <summary>Studied + MentionedOnly.</summary>
    public int Total { get; set; }
  }
}
