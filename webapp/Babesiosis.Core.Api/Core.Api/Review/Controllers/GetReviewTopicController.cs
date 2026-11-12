using Babesiosis.Core.Api.Review.Commands;
using Babesiosis.Core.Api.Review.ViewModels;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Assertions;
using Babesiosis.Core.Data;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Review.Controllers
{
  /// <summary>
  /// One topic page: the category's figures (the overview row), its study designs and
  /// periods, its narrative synthesis as written (dbo.synthesis_section) and its canine
  /// articles. An unknown code is a validation error.
  /// </summary>
  public class GetReviewTopicController
  {
    private readonly IDbContextService _dbContextService;

    public GetReviewTopicController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<ReviewTopicViewModel> HandleCommand(Guid userId, GetReviewTopicCommand command)
    {
      var code = command?.Code?.Trim().ToUpperInvariant();
      if (string.IsNullOrEmpty(code))
      {
        Assertion.Throw("A topic code is required.");
      }

      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var categories = await ReviewFacts.LoadCategoriesAsync(dbContext);
      var category = categories.FirstOrDefault(c => c.Code.Trim() == code);
      if (category == null)
      {
        Assertion.Throw($"There is no topic with the code {code}.");
      }

      var canine = await ReviewFacts.LoadCanineAsync(dbContext);
      var secondaryTags = await ReviewFacts.LoadSecondaryTagCountsAsync(dbContext);
      var synthesis = await ReviewFacts.LoadSynthesisAsync(dbContext, code);
      var articles = canine.Where(a => a.CategoryCode?.Trim() == code).ToList();

      return new ReviewTopicViewModel
      {
        Topic = ReviewFacts.TopicRow(category, canine, secondaryTags),
        CanineArticles = canine.Count,
        Periods = ReviewFacts.Periods.ToList(),
        Designs = ReviewFacts.DesignRows(articles).OrderByDescending(r => r.Articles).ToList(),
        Synthesis = synthesis.Select(ReviewFacts.ToViewModel).ToList(),
        SynthesisLoadedAt = ReviewFacts.LoadedAt(synthesis),
        Articles = articles
          .OrderByDescending(a => a.PubYear)
          .ThenBy(a => a.Code)
          .Select(a => new TopicArticleViewModel
          {
            Code = a.Code,
            Year = a.PubYear,
            Title = a.Title,
            StudyType = a.StudyType,
            InfectedDogs = a.InfectedDogs,
            Controls = a.Controls,
            Species = a.Species,
            Finding = a.Finding,
            AbstractOnly = a.AbstractOnly,
            HighConfidence = a.HighConfidence,
            SourceUrl = ReviewFacts.SourceUrl(a)
          })
          .ToList(),
        Topics = categories
          .Select(c => new TopicLinkViewModel
          {
            Code = c.Code.Trim(),
            Label = c.Label ?? c.Name,
            Name = c.Name,
            Articles = canine.Count(a => a.CategoryCode?.Trim() == c.Code.Trim())
          })
          .OrderByDescending(t => t.Articles)
          .ToList()
      };
    }
  }
}
