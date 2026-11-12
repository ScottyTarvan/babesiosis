using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>One period band of the topics table, e.g. 2006–10.</summary>
  public class PeriodViewModel
  {
    public string Label { get; set; }
    public int FromYear { get; set; }
    public int ToYear { get; set; }
  }

  /// <summary>
  /// One category's figures: the overview's topics-table row and the topic page's tiles.
  /// Canine (CB) articles whose primary category this is.
  /// </summary>
  public class TopicRowViewModel
  {
    public string Code { get; set; }
    /// <summary>Short plain-language name, e.g. "Kidney".</summary>
    public string Label { get; set; }
    /// <summary>Formal category name, e.g. "Renal injury and renal function".</summary>
    public string Name { get; set; }
    public int Articles { get; set; }
    /// <summary>Articles with no cohort plus distinct cohorts.</summary>
    public int IndependentSources { get; set; }
    /// <summary>Articles that belong to a cohort.</summary>
    public int CohortArticles { get; set; }
    /// <summary>Distinct cohorts among the articles.</summary>
    public int Cohorts { get; set; }
    /// <summary>Canine articles that carry this category as a secondary tag.</summary>
    public int SecondaryTags { get; set; }
    /// <summary>Articles per period band, in the order of the response's Periods.</summary>
    public List<int> PeriodCounts { get; set; } = new List<int>();
    /// <summary>Articles whose category label is low-confidence or a fallback.</summary>
    public int NotHighConfidence { get; set; }
    /// <summary>Articles appraised from the abstract only.</summary>
    public int AbstractOnly { get; set; }
  }

  /// <summary>One bar of a breakdown card (study design, species, country, sample size).</summary>
  public class BreakdownRowViewModel
  {
    public string Label { get; set; }
    /// <summary>The value the Articles grid filters on for this row; null when the grid cannot filter on it.</summary>
    public string FilterValue { get; set; }
    public int Articles { get; set; }
    public int? IndependentSources { get; set; }
    /// <summary>Articles published 2022–26 (species card).</summary>
    public int? RecentArticles { get; set; }
    /// <summary>Articles appraised from the abstract only (species card).</summary>
    public int? AbstractOnly { get; set; }
    /// <summary>A short note shown beside the bar, e.g. the leading species of a country.</summary>
    public string Note { get; set; }
    /// <summary>True for a "not stated" / "not reported" row, drawn in grey.</summary>
    public bool IsUnknown { get; set; }
  }

  /// <summary>One headed section of a narrative synthesis, as written (Markdown).</summary>
  public class SynthesisSectionViewModel
  {
    public string Key { get; set; }
    public string Heading { get; set; }
    public string Body { get; set; }
  }
}
