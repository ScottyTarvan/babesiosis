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
  /// Per-year article counts by study type and by Babesia species, for the Review
  /// dashboard's "Evidence profile" card.
  ///
  /// Canine (CB) articles only, on the fixed axis 2006..2026 (zero-filled). Study type
  /// and species come from <see cref="ArticleClassification"/>, the rules the Articles
  /// grid filters on too. Articles outside the year axis (or with no year) are left out.
  /// </summary>
  public class GetEvidenceProfileController
  {
    private const string CaninePrefix = "CB";
    private const int FirstYear = 2006;
    private const int LastYear = 2026;

    private static readonly string[] StudyTypeRows = ArticleClassification.StudyTypes;
    private static readonly string[] SpeciesRows = ArticleClassification.SpeciesGroups;

    private readonly IDbContextService _dbContextService;

    public GetEvidenceProfileController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<EvidenceProfileViewModel> HandleCommand(Guid userId, GetEvidenceProfileCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var articles = await dbContext.Articles
        .Where(a => a.Code.StartsWith(CaninePrefix)
          && a.PubYear >= FirstYear && a.PubYear <= LastYear)
        .Classified()
        .Select(c => new { c.Article.PubYear, c.StudyType, c.Species })
        .ToListAsync();

      var years = Enumerable.Range(FirstYear, LastYear - FirstYear + 1).ToList();
      var studyType = NewCounts(StudyTypeRows, years.Count);
      var species = NewCounts(SpeciesRows, years.Count);

      foreach (var article in articles)
      {
        int yearIndex = article.PubYear!.Value - FirstYear;
        studyType[article.StudyType][yearIndex]++;
        species[article.Species][yearIndex]++;
      }

      return new EvidenceProfileViewModel
      {
        ArticleCount = articles.Count,
        Years = years,
        Blocks = new List<EvidenceProfileBlockViewModel>
        {
          ToBlock("By study type", StudyTypeRows, studyType),
          ToBlock("By Babesia species", SpeciesRows, species)
        }
      };
    }

    private static Dictionary<string, int[]> NewCounts(IEnumerable<string> labels, int yearCount) =>
      labels.ToDictionary(label => label, _ => new int[yearCount]);

    private static EvidenceProfileBlockViewModel ToBlock(string title, IEnumerable<string> labels,
      Dictionary<string, int[]> counts) =>
      new EvidenceProfileBlockViewModel
      {
        Title = title,
        Rows = labels
          .Select(label => new EvidenceProfileRowViewModel
          {
            Label = label,
            Total = counts[label].Sum(),
            Counts = counts[label].ToList()
          })
          .ToList()
      };
  }
}
