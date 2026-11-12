using Babesiosis.Core.Api.Review.Commands;
using Babesiosis.Core.Api.Review.ViewModels;
using Babesiosis.Core.Articles;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Review.Controllers
{
  /// <summary>
  /// The Overview screen: headline figures, caveats, articles per year, one row per topic,
  /// and the study design, species, country and sample-size cards. Canine (CB) articles
  /// only; every figure is counted here from the database (see <see cref="ReviewFacts"/>).
  /// </summary>
  public class GetReviewOverviewController
  {
    private const int TopCountries = 10;

    /// <summary>Infected-dog bands for primary studies: label and inclusive bounds.</summary>
    private static readonly (string Label, int From, int To)[] SizeBands =
    {
      ("1–9", 1, 9), ("10–19", 10, 19), ("20–49", 20, 49), ("50–99", 50, 99), ("100 or more", 100, int.MaxValue)
    };

    private readonly IDbContextService _dbContextService;

    public GetReviewOverviewController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<ReviewOverviewViewModel> HandleCommand(Guid userId, GetReviewOverviewCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var canine = await ReviewFacts.LoadCanineAsync(dbContext);
      var categories = await ReviewFacts.LoadCategoriesAsync(dbContext);
      var secondaryTags = await ReviewFacts.LoadSecondaryTagCountsAsync(dbContext);
      int backgroundArticles = await dbContext.Articles.CountAsync(a => a.Code.StartsWith(ReviewFacts.BackgroundPrefix));
      int countrySpellings = await dbContext.Articles
        .Where(a => a.Code.StartsWith(ReviewFacts.CaninePrefix) && a.Country != null)
        .Select(a => a.Country).Distinct().CountAsync();

      var primary = canine.Where(a => a.IncludeType == "primary").ToList();

      return new ReviewOverviewViewModel
      {
        Summary = new ReviewSummaryViewModel
        {
          CanineArticles = canine.Count,
          PrimaryStudies = primary.Count,
          CaseReports = canine.Count(a => a.IncludeType == "case_report"),
          Reviews = canine.Count(a => a.IncludeType == "review"),
          IndependentSources = ReviewFacts.IndependentSources(canine),
          Cohorts = canine.Where(a => !string.IsNullOrEmpty(a.CohortId)).Select(a => a.CohortId).Distinct().Count(),
          CohortArticles = canine.Count(a => !string.IsNullOrEmpty(a.CohortId)),
          FullText = canine.Count(a => a.TextSource == "jats_xml" || a.TextSource == "pdf"),
          AbstractOnly = canine.Count(a => a.AbstractOnly),
          HighConfidence = canine.Count(a => a.CategoryConfidence == "high"),
          LowConfidence = canine.Count(a => a.CategoryConfidence == "low"),
          FallbackLabels = canine.Count(a => a.CategoryConfidence != "high" && a.CategoryConfidence != "low"),
          Uncategorised = canine.Count(a => a.CategoryCode == null),
          MedianInfectedDogs = ReviewFacts.Median(primary.Where(a => a.InfectedDogs > 0).Select(a => a.InfectedDogs.Value)),
          PrimaryStudiesWithSize = primary.Count(a => a.InfectedDogs > 0),
          PrimaryStudiesWithControls = primary.Count(a => a.Controls > 0),
          BackgroundArticles = backgroundArticles,
          Countries = canine.Where(a => a.Country != null).Select(a => a.Country).Distinct(StringComparer.OrdinalIgnoreCase).Count(),
          CountrySpellings = countrySpellings,
          FirstYear = ReviewFacts.FirstYear,
          LastYear = ReviewFacts.LastYear
        },
        Years = Enumerable.Range(ReviewFacts.FirstYear, ReviewFacts.LastYear - ReviewFacts.FirstYear + 1)
          .Select(year =>
          {
            var rows = canine.Where(a => a.PubYear == year).ToList();
            return new YearCountViewModel
            {
              Year = year,
              Articles = rows.Count,
              IndependentSources = ReviewFacts.IndependentSources(rows),
              Partial = ReviewFacts.PartialYears.Contains(year)
            };
          })
          .ToList(),
        Periods = ReviewFacts.Periods.ToList(),
        Topics = categories
          .Select(c => ReviewFacts.TopicRow(c, canine, secondaryTags))
          .OrderByDescending(t => t.Articles)
          .ThenBy(t => categories.FindIndex(c => c.Code.Trim() == t.Code))
          .ToList(),
        Designs = ReviewFacts.DesignRows(canine).OrderByDescending(r => r.Articles).ToList(),
        Species = SpeciesRows(canine),
        Countries = CountryRows(canine),
        SampleSizes = SizeRows(primary)
      };
    }

    private static List<BreakdownRowViewModel> SpeciesRows(List<ArticleFact> canine) =>
      ArticleClassification.SpeciesGroups
        .Select(label =>
        {
          var rows = canine.Where(a => a.Species == label).ToList();
          return new BreakdownRowViewModel
          {
            Label = label,
            FilterValue = label,
            Articles = rows.Count,
            IndependentSources = ReviewFacts.IndependentSources(rows),
            RecentArticles = rows.Count(a => a.PubYear >= ReviewFacts.RecentFromYear),
            AbstractOnly = rows.Count(a => a.AbstractOnly),
            IsUnknown = label == ArticleClassification.NotIdentified
          };
        })
        .ToList();

    /// <summary>The top countries by article count, each with its leading species, then "Not stated".</summary>
    private static List<BreakdownRowViewModel> CountryRows(List<ArticleFact> canine)
    {
      var rows = canine
        .Where(a => a.Country != null)
        .GroupBy(a => a.Country, StringComparer.OrdinalIgnoreCase)
        .OrderByDescending(g => g.Count())
        .ThenBy(g => g.Key)
        .Take(TopCountries)
        .Select(g =>
        {
          var leading = g.GroupBy(a => a.Species).OrderByDescending(s => s.Count()).ThenBy(s => s.Key).First();
          var note = leading.Key == ArticleClassification.NotIdentified
            ? $"species not identified in {leading.Count()}"
            : $"{leading.Key} in {leading.Count()}";
          return new BreakdownRowViewModel
          {
            Label = g.Key,
            FilterValue = g.Key,
            Articles = g.Count(),
            IndependentSources = ReviewFacts.IndependentSources(g),
            Note = note
          };
        })
        .ToList();

      var notStated = canine.Where(a => a.Country == null).ToList();
      rows.Add(new BreakdownRowViewModel
      {
        Label = "Not stated",
        Articles = notStated.Count,
        IndependentSources = ReviewFacts.IndependentSources(notStated),
        Note = $"{notStated.Count(a => a.AbstractOnly)} read as abstract only",
        IsUnknown = true
      });
      return rows;
    }

    /// <summary>Primary studies by infected dogs, in bands, then "Not reported" (missing or zero).</summary>
    private static List<BreakdownRowViewModel> SizeRows(List<ArticleFact> primary)
    {
      var rows = SizeBands
        .Select(band => new BreakdownRowViewModel
        {
          Label = band.Label,
          Articles = primary.Count(a => a.InfectedDogs >= band.From && a.InfectedDogs <= band.To)
        })
        .ToList();
      rows.Add(new BreakdownRowViewModel
      {
        Label = "Not reported",
        Articles = primary.Count(a => !(a.InfectedDogs > 0)),
        IsUnknown = true
      });
      return rows;
    }
  }
}
