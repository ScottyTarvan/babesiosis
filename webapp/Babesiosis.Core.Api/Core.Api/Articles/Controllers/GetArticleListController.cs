using Babesiosis.Core.Api.Articles.Commands;
using Babesiosis.Core.Api.Articles.ViewModels;
using Babesiosis.Core.Articles;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Articles;
using Babesiosis.Core.ViewModels;
using DevExtreme.AspNet.Data;
using Microsoft.EntityFrameworkCore;
using System;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Articles.Controllers
{
  /// <summary>
  /// Every loaded article, one page at a time, in the standard
  /// <c>{ page, permissions }</c> envelope. The screen is read-only, so the
  /// capability echo is empty.
  ///
  /// Rows are projected before paging so the wide narrative, markdown and
  /// embedding columns never leave the database, and so the grid's sort and
  /// filter selectors resolve against <see cref="ArticleViewModel"/>, including the
  /// study-type and species labels, which <see cref="ArticleClassification"/>
  /// computes in SQL so the grid can filter on them. The
  /// projection is an <see cref="ArticleRow"/>, a view model plus the two
  /// columns the source link is resolved from; the resolved rows go out as
  /// plain view models so those columns stay off the wire.
  /// </summary>
  public class GetArticleListController
  {
    const int DefaultPageSize = 500;

    /// <summary>A grid row with the inputs of <see cref="ArticleSourceLink.Resolve"/> that the row itself does not carry.</summary>
    private sealed class ArticleRow : ArticleViewModel
    {
      public string FulltextUrl { get; set; }
      public string SourceLinks { get; set; }

      public ArticleViewModel ToViewModel() => new ArticleViewModel
      {
        Id = Id,
        Code = Code,
        PubDate = PubDate,
        PubDatePrecision = PubDatePrecision,
        CategoryName = CategoryName,
        CategoryCode = CategoryCode,
        CategoryLabel = CategoryLabel,
        StudyType = StudyType,
        Species = Species,
        Country = Country,
        Journal = Journal,
        Title = Title,
        Summary = Summary,
        Doi = Doi,
        Pmid = Pmid,
        SourceUrl = ArticleSourceLink.Resolve(Doi, Pmid, SourceLinks, FulltextUrl)
      };
    }

    private readonly IDbContextService _dbContextService;

    public GetArticleListController(IDbContextService dbContextService)
    {
      _dbContextService = dbContextService;
    }

    public async Task<ItemsViewModel<ArticleViewModel>> HandleCommand(Guid userId, GetArticleListCommand command)
    {
      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();

      var loadOptions = command?.LoadOptions ?? new DataSourceLoadOptionsBase();
      if (loadOptions.Take <= 0)
      {
        loadOptions.Take = DefaultPageSize;
      }

      var query = dbContext.Articles
        .AsNoTracking()
        .Classified()
        .Select(c => new ArticleRow
        {
          Id = c.Article.Id,
          Code = c.Article.Code,
          PubDate = c.Article.PubDate,
          PubDatePrecision = c.Article.PubDatePrecision == DatePrecision.Year ? "Y"
            : c.Article.PubDatePrecision == DatePrecision.Month ? "M"
            : "D",
          CategoryName = c.Article.PrimaryCategory.Name,
          CategoryCode = c.Article.PrimaryCategory.Code,
          CategoryLabel = c.Article.PrimaryCategory.Label,
          StudyType = c.StudyType,
          Species = c.Species,
          Country = c.Article.CountryNormalised,
          Journal = c.Article.Journal,
          Title = c.Article.Title,
          Summary = c.Article.OneSentenceFinding,
          Doi = c.Article.Doi,
          Pmid = c.Article.Pmid,
          FulltextUrl = c.Article.FulltextUrl,
          SourceLinks = c.Article.SourceLinks
        });

      // Newest first unless the grid asks otherwise; paging needs a stable order.
      if (loadOptions.Sort == null || loadOptions.Sort.Length == 0)
      {
        query = query.OrderByDescending(a => a.PubDate).ThenBy(a => a.Id);
      }

      var page = await loadOptions.LoadPageAsync(query);

      return new ItemsViewModel<ArticleViewModel>
      {
        Page = new PagedItemsViewModel<ArticleViewModel>
        {
          Items = page.Results.Select(row => row.ToViewModel()).ToList(),
          Paging = new PagingViewModel(page.TotalRecordCount, loadOptions.Skip, loadOptions.Take)
        }
      };
    }
  }
}
