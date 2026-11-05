using Babesiosis.Core.Api.Experiments.Commands;
using Babesiosis.Core.Api.Experiments.ViewModels;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Experiments.Controllers
{
  /// <summary>
  /// Every experiment run with its dataset and article, newest run first. The finding
  /// count is computed in the database so the panel can show it without loading rows.
  /// </summary>
  public class GetExperimentListController
  {
    private readonly IDbContextService _dbContextService;

    public GetExperimentListController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<ExperimentListViewModel> HandleCommand(Guid userId, GetExperimentListCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var query = dbContext.Experiments.AsNoTracking();
      if (!string.IsNullOrWhiteSpace(command?.DatasetCode))
      {
        query = query.Where(e => e.Dataset.Code == command.DatasetCode);
      }

      var items = await query
        .OrderByDescending(e => e.RunAt)
        .ThenBy(e => e.Code)
        .Select(e => new ExperimentListItemViewModel
        {
          Code = e.Code,
          Name = e.Name,
          Method = e.Method,
          DatasetCode = e.Dataset.Code,
          DatasetTitle = e.Dataset.Title,
          ArticleCode = e.Dataset.ArticleCode,
          ArticleTitle = e.Dataset.Article.Title,
          RunAt = e.RunAt,
          SubjectCount = e.SubjectCount,
          VariableCount = e.VariableCount,
          TestCount = e.TestCount,
          FindingCount = e.Associations.Count(a => a.Significant && !a.Trivial),
          Summary = e.Summary
        })
        .ToListAsync();

      return new ExperimentListViewModel
      {
        Items = items,
        DatasetCount = items.Select(i => i.DatasetCode).Where(c => c != null).Distinct().Count()
      };
    }
  }
}
