using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>
  /// The Overview screen: the size and shape of the canine (CB) literature. Every figure is
  /// counted from the database on request.
  /// </summary>
  public class ReviewOverviewViewModel
  {
    public ReviewSummaryViewModel Summary { get; set; } = new ReviewSummaryViewModel();
    public List<YearCountViewModel> Years { get; set; } = new List<YearCountViewModel>();
    public List<PeriodViewModel> Periods { get; set; } = new List<PeriodViewModel>();
    /// <summary>One row per category, most articles first.</summary>
    public List<TopicRowViewModel> Topics { get; set; } = new List<TopicRowViewModel>();
    public List<BreakdownRowViewModel> Designs { get; set; } = new List<BreakdownRowViewModel>();
    public List<BreakdownRowViewModel> Species { get; set; } = new List<BreakdownRowViewModel>();
    /// <summary>The top ten countries, then "Not stated".</summary>
    public List<BreakdownRowViewModel> Countries { get; set; } = new List<BreakdownRowViewModel>();
    /// <summary>Infected dogs per primary study, in bands, then "Not reported".</summary>
    public List<BreakdownRowViewModel> SampleSizes { get; set; } = new List<BreakdownRowViewModel>();
  }

  /// <summary>The headline tiles and the caveats box.</summary>
  public class ReviewSummaryViewModel
  {
    public int CanineArticles { get; set; }
    /// <summary>include_type primary.</summary>
    public int PrimaryStudies { get; set; }
    public int CaseReports { get; set; }
    public int Reviews { get; set; }
    public int IndependentSources { get; set; }
    public int Cohorts { get; set; }
    public int CohortArticles { get; set; }
    /// <summary>Read in full text (JATS XML or PDF).</summary>
    public int FullText { get; set; }
    public int AbstractOnly { get; set; }
    public int HighConfidence { get; set; }
    public int LowConfidence { get; set; }
    /// <summary>NLP found no category; the extraction agent's label was kept.</summary>
    public int FallbackLabels { get; set; }
    /// <summary>Canine articles with no primary category.</summary>
    public int Uncategorised { get; set; }
    public double? MedianInfectedDogs { get; set; }
    /// <summary>Primary studies that state the number of infected dogs.</summary>
    public int PrimaryStudiesWithSize { get; set; }
    /// <summary>Primary studies that state a control group.</summary>
    public int PrimaryStudiesWithControls { get; set; }
    /// <summary>Background (BG) articles in the database, not counted anywhere on the screen.</summary>
    public int BackgroundArticles { get; set; }
    /// <summary>Distinct countries after tidying.</summary>
    public int Countries { get; set; }
    /// <summary>Distinct raw country strings before tidying.</summary>
    public int CountrySpellings { get; set; }
    public int FirstYear { get; set; }
    public int LastYear { get; set; }
  }

  /// <summary>Canine articles published in one year.</summary>
  public class YearCountViewModel
  {
    public int Year { get; set; }
    public int Articles { get; set; }
    public int IndependentSources { get; set; }
    /// <summary>The window starts and ends 23 October, so the first and last years are partial.</summary>
    public bool Partial { get; set; }
  }
}
