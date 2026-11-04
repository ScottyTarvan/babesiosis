using Babesiosis.Core.Api.Review.Commands;
using Babesiosis.Core.Api.Review.ViewModels;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Review.Controllers
{
  /// <summary>
  /// Article counts per clinical syndrome or sign, for the Review dashboard's
  /// "Clinical syndromes and signs" card.
  ///
  /// Counts canine (CB) articles only. Terms hidden by the curated display map
  /// (core/data/terms/term_display.csv) are left out; terms that share a display
  /// name are merged and each article counts once per name. An article "studied"
  /// a term when any of its rows for that name is studied; otherwise it only
  /// mentioned it.
  /// </summary>
  public class GetTermCountsController
  {
    private const string CaninePrefix = "CB";
    private const string AbstractOnlySource = "abstract";
    private const int MaxTop = 100;

    private readonly IDbContextService _dbContextService;

    public GetTermCountsController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<TermCountsViewModel> HandleCommand(Guid userId, GetTermCountsCommand command)
    {
      int top = Math.Clamp(command?.Top ?? 20, 1, MaxTop);

      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var counts = await dbContext.ArticleTerms
        .Where(at => at.Article.Code.StartsWith(CaninePrefix) && !at.Term.Hidden)
        .GroupBy(at => at.Term.DisplayName ?? at.Term.Concept)
        .Select(g => new
        {
          Name = g.Key,
          Total = g.Select(at => at.ArticleId).Distinct().Count(),
          Studied = g.Where(at => at.Studied).Select(at => at.ArticleId).Distinct().Count()
        })
        .OrderByDescending(c => c.Total)
        .ThenByDescending(c => c.Studied)
        .ThenBy(c => c.Name)
        .Take(top)
        .ToListAsync();

      var articles = dbContext.Articles
        .Where(a => a.Code.StartsWith(CaninePrefix) && a.ArticleTerms.Any());

      return new TermCountsViewModel
      {
        ArticleCount = await articles.CountAsync(),
        AbstractOnlyCount = await articles.CountAsync(a => a.TextSource == AbstractOnlySource),
        Terms = counts
          .Select(c => new TermCountsRowViewModel
          {
            Name = c.Name,
            Studied = c.Studied,
            MentionedOnly = c.Total - c.Studied,
            Total = c.Total
          })
          .ToList()
      };
    }
  }
}
