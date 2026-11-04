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
  /// Article counts per primary category per publication year, for the Review
  /// dashboard heat map.
  ///
  /// Only articles with both a primary category and a publication year are
  /// counted; secondary and comparator tags are not. Every category is returned,
  /// including one with no articles, so the heat map always shows the full list.
  /// </summary>
  public class GetCategoryYearCountsController
  {
    private readonly IDbContextService _dbContextService;

    public GetCategoryYearCountsController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<CategoryYearCountsViewModel> HandleCommand(Guid userId, GetCategoryYearCountsCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var categories = await dbContext.Categories
        .OrderBy(c => c.SortOrder)
        .Select(c => new { c.Id, c.Code, c.Name, c.Label })
        .ToListAsync();

      var counts = await dbContext.Articles
        .Where(a => a.PrimaryCategoryId != null && a.PubYear != null)
        .GroupBy(a => new { CategoryId = a.PrimaryCategoryId.Value, Year = a.PubYear.Value })
        .Select(g => new { g.Key.CategoryId, g.Key.Year, Count = g.Count() })
        .ToListAsync();

      var result = new CategoryYearCountsViewModel();
      if (counts.Count > 0)
      {
        int firstYear = counts.Min(c => c.Year);
        int lastYear = counts.Max(c => c.Year);
        result.Years = Enumerable.Range(firstYear, lastYear - firstYear + 1).ToList();
      }

      var countLookup = counts.ToDictionary(c => (c.CategoryId, (int)c.Year), c => c.Count);

      result.Categories = categories
        .Select(c => new CategoryYearCountsRowViewModel
        {
          Code = c.Code,
          Name = c.Name,
          Label = c.Label,
          Counts = result.Years
            .Select(year => countLookup.TryGetValue((c.Id, year), out int count) ? count : 0)
            .ToList()
        })
        .ToList();

      return result;
    }
  }
}
