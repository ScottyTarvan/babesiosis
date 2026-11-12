using Babesiosis.Core.Api.Review.Commands;
using Babesiosis.Core.Api.Review.ViewModels;
using Babesiosis.Core.Articles;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Review.Controllers
{
  /// <summary>
  /// The Gaps and questions screen: the category × study-design matrix of canine articles,
  /// four gap figures computed from it, and the cross-cutting themes (CROSS.md) and research
  /// questions (QUESTIONS.md) as written.
  /// </summary>
  public class GetReviewGapsController
  {
    private const string CrossDocument = "CROSS";
    private const string QuestionsDocument = "QUESTIONS";

    private readonly IDbContextService _dbContextService;

    public GetReviewGapsController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<ReviewGapsViewModel> HandleCommand(Guid userId, GetReviewGapsCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var canine = await ReviewFacts.LoadCanineAsync(dbContext);
      var categories = await ReviewFacts.LoadCategoriesAsync(dbContext);
      var secondaryTags = await ReviewFacts.LoadSecondaryTagCountsAsync(dbContext);
      var synthesis = await ReviewFacts.LoadSynthesisAsync(dbContext, CrossDocument, QuestionsDocument);

      var designs = ArticleClassification.StudyTypes.ToList();
      var rows = categories
        .Select(c =>
        {
          var code = c.Code.Trim();
          var articles = canine.Where(a => a.CategoryCode?.Trim() == code).ToList();
          return new GapRowViewModel
          {
            Code = code,
            Label = c.Label ?? c.Name,
            Name = c.Name,
            Counts = designs.Select(d => articles.Count(a => a.StudyType == d)).ToList(),
            Total = articles.Count
          };
        })
        .OrderByDescending(r => r.Total)
        .ToList();

      return new ReviewGapsViewModel
      {
        Designs = designs,
        Rows = rows,
        CanineArticles = canine.Count,
        Figures = Figures(canine, rows, designs, secondaryTags),
        Themes = synthesis
          .Where(s => s.DocumentCode == CrossDocument && s.SectionKey.StartsWith("theme-"))
          .Select(ReviewFacts.ToViewModel)
          .ToList(),
        Questions = synthesis
          .Where(s => s.DocumentCode == QuestionsDocument && s.SectionKey.Length > 1 && s.SectionKey[0] == 'q'
            && s.SectionKey.Skip(1).All(char.IsDigit))
          .Select(ReviewFacts.ToViewModel)
          .ToList(),
        SynthesisLoadedAt = ReviewFacts.LoadedAt(synthesis)
      };
    }

    private static List<GapFigureViewModel> Figures(List<ArticleFact> canine, List<GapRowViewModel> rows,
      List<string> designs, IReadOnlyDictionary<string, int> secondaryTags)
    {
      int prognosticIndex = designs.IndexOf(ArticleClassification.Prognostic);
      int mechanisticIndex = designs.IndexOf(ArticleClassification.Mechanistic);
      int prognostic = rows.Sum(r => r.Counts[prognosticIndex]);
      int mechanistic = rows.Sum(r => r.Counts[mechanisticIndex]);
      var noPrognostic = rows.Where(r => r.Counts[prognosticIndex] == 0).Select(r => r.Label).ToList();
      var noMechanistic = rows.Where(r => r.Counts[mechanisticIndex] == 0).Select(r => r.Label).ToList();
      var topMechanistic = rows.OrderByDescending(r => r.Counts[mechanisticIndex]).First();

      var smallest = rows.Where(r => r.Total > 0).OrderBy(r => r.Total).Take(2).ToList();
      int smallestArticles = smallest.Sum(r => r.Total);
      int smallestTags = smallest.Sum(r => secondaryTags.TryGetValue(r.Code, out var n) ? n : 0);

      int noSpecies = canine.Count(a => a.Species == ArticleClassification.NotIdentified);

      return new List<GapFigureViewModel>
      {
        new GapFigureViewModel
        {
          Key = "prognostic",
          Value = prognostic.ToString(),
          Title = "prognostic studies in 20 years",
          Text = $"Of {canine.Count} canine articles."
            + (noPrognostic.Count > 0 ? $" {Sentence(noPrognostic)} {(noPrognostic.Count == 1 ? "has" : "have")} none." : "")
        },
        new GapFigureViewModel
        {
          Key = "mechanistic",
          Value = mechanistic.ToString(),
          Title = "mechanistic or experimental studies",
          Text = $"{topMechanistic.Counts[mechanisticIndex]} are on {topMechanistic.Label.ToLowerInvariant()}."
            + (noMechanistic.Count > 0 ? $" {Sentence(noMechanistic)} {(noMechanistic.Count == 1 ? "has" : "have")} none." : "")
        },
        new GapFigureViewModel
        {
          Key = "smallest-topics",
          Value = smallestArticles.ToString(),
          Title = $"articles with {Sentence(smallest.Select(r => r.Label.ToLowerInvariant()).ToList(), "or")} as main topic",
          Text = $"They are tagged {smallestTags} times as a secondary topic"
            + (smallestTags > smallestArticles ? ": mentioned often, studied rarely." : ".")
        },
        new GapFigureViewModel
        {
          Key = "no-species",
          Value = noSpecies.ToString(),
          Title = "articles with no species identified in the text read",
          Text = $"{Percent(noSpecies, canine.Count)}% of the canine articles, so species comparisons rest on fewer studies than the totals suggest."
        }
      };
    }

    /// <summary>
    /// "A", "A and b", "A; b; and c": labels after the first are lower-cased to read as one
    /// sentence. Three or more are separated by semicolons, since the labels hold "and" themselves.
    /// </summary>
    private static string Sentence(List<string> items, string conjunction = "and")
    {
      if (items.Count <= 1)
      {
        return items.FirstOrDefault() ?? "";
      }
      var rest = items.Skip(1).Select(i => i.ToLowerInvariant()).ToList();
      if (items.Count == 2)
      {
        return $"{items[0]} {conjunction} {rest[0]}";
      }
      var head = string.Join("; ", new[] { items[0] }.Concat(rest.Take(rest.Count - 1)));
      return $"{head}; {conjunction} {rest[^1]}";
    }

    private static int Percent(int part, int whole) => whole == 0 ? 0 : (int)Math.Round(100.0 * part / whole);
  }
}
