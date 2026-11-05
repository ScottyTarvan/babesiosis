using Babesiosis.Core.Api.Articles;
using Babesiosis.Core.Api.Experiments.Commands;
using Babesiosis.Core.Api.Experiments.ViewModels;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using Babesiosis.Core.Exceptions;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Experiments.Controllers
{
  /// <summary>
  /// One experiment in full. Four queries: the header with its dataset and article, the
  /// dataset's variable dictionary, the association rows (filtered and capped by the command,
  /// best adjusted p first) and the result payloads. Counts of findings are taken over every
  /// association of the run, so the header is right even when the rows are capped.
  /// </summary>
  public class GetExperimentDetailController
  {
    private const int MaxAssociationsCap = 50000;

    private readonly IDbContextService _dbContextService;

    public GetExperimentDetailController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<ExperimentDetailViewModel> HandleCommand(Guid userId, GetExperimentDetailCommand command)
    {
      if (string.IsNullOrWhiteSpace(command?.Code))
      {
        throw new ValidationException("An experiment code is required.");
      }

      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var header = await dbContext.Experiments.AsNoTracking()
        .Where(e => e.Code == command.Code)
        .Select(e => new
        {
          e.Id,
          e.Code,
          e.Name,
          e.Description,
          e.Method,
          e.Parameters,
          e.Script,
          e.ScriptVersion,
          e.RunAt,
          e.SubjectCount,
          e.VariableCount,
          e.TestCount,
          e.Summary,
          DatasetId = (int?)e.Dataset.Id,
          Dataset = e.Dataset == null ? null : new
          {
            e.Dataset.Code,
            e.Dataset.Title,
            e.Dataset.ArticleCode,
            ArticleTitle = e.Dataset.Article.Title,
            ArticleDoi = e.Dataset.Article.Doi,
            ArticlePmid = e.Dataset.Article.Pmid,
            ArticleSourceLinks = e.Dataset.Article.SourceLinks,
            ArticleFulltextUrl = e.Dataset.Article.FulltextUrl,
            e.Dataset.Repository,
            e.Dataset.SourceRecord,
            e.Dataset.Licence,
            e.Dataset.IndependentSource,
            e.Dataset.Species,
            e.Dataset.SubjectCount,
            e.Dataset.Notes
          },
          FindingCount = e.Associations.Count(a => a.Significant && !a.Trivial),
          SignificantCount = e.Associations.Count(a => a.Significant)
        })
        .FirstOrDefaultAsync();

      if (header == null)
      {
        throw new ValidationException($"No experiment has the code '{command.Code}'.");
      }

      var variables = header.DatasetId == null
        ? new System.Collections.Generic.List<ExperimentVariableViewModel>()
        : await dbContext.Variables.AsNoTracking()
            .Where(v => v.DatasetId == header.DatasetId)
            .OrderBy(v => v.SortOrder)
            .Select(v => new ExperimentVariableViewModel
            {
              Code = v.Code,
              Name = v.Name,
              Unit = v.Unit,
              DataType = v.DataType,
              Domain = v.Domain,
              Derived = v.Derived,
              DerivedFrom = v.DerivedFrom,
              IncludeDefault = v.IncludeDefault,
              RefLow = v.RefLow,
              RefHigh = v.RefHigh,
              Description = v.Description,
              Levels = v.Levels
            })
            .ToListAsync();

      var associationQuery = dbContext.Associations.AsNoTracking()
        .Where(a => a.ExperimentId == header.Id);
      if (command.SignificantOnly)
      {
        associationQuery = associationQuery.Where(a => a.Significant);
      }
      if (!command.IncludeTrivial)
      {
        associationQuery = associationQuery.Where(a => !a.Trivial);
      }

      int cap = Math.Clamp(command.MaxAssociations <= 0 ? 5000 : command.MaxAssociations, 1, MaxAssociationsCap);
      var associations = await associationQuery
        .OrderBy(a => a.PAdjusted)
        .ThenByDescending(a => a.Estimate == null ? 0 : Math.Abs(a.Estimate.Value))
        .Take(cap + 1)
        .Select(a => new ExperimentAssociationViewModel
        {
          VariableA = a.VariableA.Code,
          VariableAName = a.VariableA.Name,
          VariableB = a.VariableB.Code,
          VariableBName = a.VariableB.Name,
          Test = a.Test,
          Estimate = a.Estimate,
          EstimateLabel = a.EstimateLabel,
          N = a.N,
          PValue = a.PValue,
          PAdjusted = a.PAdjusted,
          Significant = a.Significant,
          Trivial = a.Trivial,
          Direction = a.Direction,
          Detail = a.Detail
        })
        .ToListAsync();
      bool truncated = associations.Count > cap;
      if (truncated)
      {
        associations.RemoveAt(associations.Count - 1);
      }

      var results = await dbContext.ExperimentResults.AsNoTracking()
        .Where(r => r.ExperimentId == header.Id)
        .OrderBy(r => r.SortOrder)
        .Select(r => new ExperimentResultViewModel
        {
          Kind = r.Kind,
          Title = r.Title,
          Payload = r.Payload,
          SortOrder = r.SortOrder
        })
        .ToListAsync();

      return new ExperimentDetailViewModel
      {
        Code = header.Code,
        Name = header.Name,
        Description = header.Description,
        Method = header.Method,
        Parameters = header.Parameters,
        Script = header.Script,
        ScriptVersion = header.ScriptVersion,
        RunAt = header.RunAt,
        SubjectCount = header.SubjectCount,
        VariableCount = header.VariableCount,
        TestCount = header.TestCount,
        FindingCount = header.FindingCount,
        SignificantCount = header.SignificantCount,
        Summary = header.Summary,
        Dataset = header.Dataset == null ? null : new ExperimentDatasetViewModel
        {
          Code = header.Dataset.Code,
          Title = header.Dataset.Title,
          ArticleCode = header.Dataset.ArticleCode,
          ArticleTitle = header.Dataset.ArticleTitle,
          ArticleSourceUrl = header.Dataset.ArticleTitle == null
            ? null
            : ArticleSourceLink.Resolve(header.Dataset.ArticleDoi, header.Dataset.ArticlePmid,
                header.Dataset.ArticleSourceLinks, header.Dataset.ArticleFulltextUrl),
          Repository = header.Dataset.Repository,
          SourceRecord = header.Dataset.SourceRecord,
          Licence = header.Dataset.Licence,
          IndependentSource = header.Dataset.IndependentSource,
          Species = header.Dataset.Species,
          SubjectCount = header.Dataset.SubjectCount,
          Notes = header.Dataset.Notes
        },
        Variables = variables,
        Associations = associations,
        AssociationsTruncated = truncated,
        Results = results
      };
    }
  }
}
