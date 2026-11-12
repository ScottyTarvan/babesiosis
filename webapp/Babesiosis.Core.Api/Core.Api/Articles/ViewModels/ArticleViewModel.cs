using System;

namespace Babesiosis.Core.Api.Articles.ViewModels
{
  /// <summary>
  /// One row of the Articles list. Grid sort selectors name these properties,
  /// so a rename here is a rename on the wire too.
  /// </summary>
  public class ArticleViewModel
  {
    public int Id { get; set; }
    /// <summary>Review code, e.g. CB001.</summary>
    public string Code { get; set; }
    /// <summary>The first day of the known period; see <see cref="PubDatePrecision"/>.</summary>
    public DateOnly? PubDate { get; set; }
    /// <summary>"Y", "M" or "D": how much of <see cref="PubDate"/> is known, so the grid can show "2019" rather than "1 Jan 2019".</summary>
    public string PubDatePrecision { get; set; }
    /// <summary>The primary category's name. Null when the article has no primary category.</summary>
    public string CategoryName { get; set; }
    /// <summary>The primary category's code, e.g. REN. Null when the article has no primary category.</summary>
    public string CategoryCode { get; set; }
    /// <summary>The primary category's short label, e.g. Kidney. Null when the article has no primary category.</summary>
    public string CategoryLabel { get; set; }
    /// <summary>One of <c>ArticleClassification.StudyTypes</c>: Descriptive, Associational, Mechanistic / experimental, Prognostic, Case reports or Reviews.</summary>
    public string StudyType { get; set; }
    /// <summary>One of <c>ArticleClassification.SpeciesGroups</c>: B. canis, B. gibsoni, B. rossi, B. vogeli, Multiple species, Other named species or Not identified in text read.</summary>
    public string Species { get; set; }
    /// <summary>The study country, tidied (article.country_normalised). Null when none is stated.</summary>
    public string Country { get; set; }
    public string Journal { get; set; }
    public string Title { get; set; }
    /// <summary>The article's one-sentence finding.</summary>
    public string Summary { get; set; }
    /// <summary>Bare DOI, e.g. 10.1186/s13071-017-2106-8. Null when the article has none.</summary>
    public string Doi { get; set; }
    /// <summary>PubMed identifier. Null when the article is not in PubMed.</summary>
    public string Pmid { get; set; }
    /// <summary>
    /// Where to open the article outside this application; see
    /// <see cref="ArticleSourceLink"/> for the order of preference. Null when no
    /// source is known, in which case the title is shown as plain text.
    /// </summary>
    public string SourceUrl { get; set; }
  }
}
