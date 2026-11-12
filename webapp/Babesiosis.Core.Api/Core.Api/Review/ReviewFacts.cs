using Babesiosis.Core.Api.Articles;
using Babesiosis.Core.Api.Review.ViewModels;
using Babesiosis.Core.Articles;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Review
{
  /// <summary>One canine (CB) article with the fields the overview, topic and gaps screens count on.</summary>
  public class ArticleFact
  {
    public string Code { get; set; }
    public short? PubYear { get; set; }
    public string Title { get; set; }
    public string CohortId { get; set; }
    /// <summary>abstract, jats_xml or pdf.</summary>
    public string TextSource { get; set; }
    /// <summary>primary, case_report or review.</summary>
    public string IncludeType { get; set; }
    public int? InfectedDogs { get; set; }
    public int? Controls { get; set; }
    public string CategoryCode { get; set; }
    public string CategoryConfidence { get; set; }
    public string Country { get; set; }
    public string StudyType { get; set; }
    public string Species { get; set; }
    public string Finding { get; set; }
    public string Doi { get; set; }
    public string Pmid { get; set; }
    public string FulltextUrl { get; set; }
    public string SourceLinks { get; set; }

    public bool AbstractOnly => TextSource == "abstract";
    public bool HighConfidence => CategoryConfidence == "high";
  }

  /// <summary>
  /// The counting rules shared by the Review screens (overview, topic pages, gaps).
  ///
  /// Canine (CB) articles only. Articles are not independent evidence: an article's
  /// <c>cohort_id</c> names the cohort it reports on, so "independent sources" are the
  /// articles with no cohort plus the distinct cohorts. Study type and species come from
  /// <see cref="ArticleClassification"/>. Categories, study types and species were assigned
  /// by NLP and extraction agents, with no human review.
  /// </summary>
  public static class ReviewFacts
  {
    public const string CaninePrefix = "CB";
    public const string BackgroundPrefix = "BG";
    public const int FirstYear = 2006;
    public const int LastYear = 2026;
    /// <summary>The review window runs 23 October to 23 October, so the first and last years are partial.</summary>
    public static readonly int[] PartialYears = { FirstYear, LastYear };
    /// <summary>"Recent" for the species card's share column.</summary>
    public const int RecentFromYear = 2022;

    /// <summary>The four period bands of the topics table, last one six calendar years.</summary>
    public static readonly PeriodViewModel[] Periods =
    {
      new PeriodViewModel { Label = "2006–10", FromYear = 2006, ToYear = 2010 },
      new PeriodViewModel { Label = "2011–15", FromYear = 2011, ToYear = 2015 },
      new PeriodViewModel { Label = "2016–20", FromYear = 2016, ToYear = 2020 },
      new PeriodViewModel { Label = "2021–26", FromYear = 2021, ToYear = 2026 },
    };

    /// <summary>Every CB article, classified, with the columns the screens need (the wide text columns stay in the database).</summary>
    public static Task<List<ArticleFact>> LoadCanineAsync(ArticlesDbContext dbContext) =>
      dbContext.Articles
        .AsNoTracking()
        .Where(a => a.Code.StartsWith(CaninePrefix))
        .Classified()
        .Select(c => new ArticleFact
        {
          Code = c.Article.Code,
          PubYear = c.Article.PubYear,
          Title = c.Article.Title,
          CohortId = c.Article.CohortId,
          TextSource = c.Article.TextSource,
          IncludeType = c.Article.IncludeType,
          InfectedDogs = c.Article.InfectedDogCount,
          Controls = c.Article.ControlCount,
          CategoryCode = c.Article.PrimaryCategory.Code,
          CategoryConfidence = c.Article.CategoryConfidence,
          Country = c.Article.CountryNormalised,
          StudyType = c.StudyType,
          Species = c.Species,
          Finding = c.Article.OneSentenceFinding,
          Doi = c.Article.Doi,
          Pmid = c.Article.Pmid,
          FulltextUrl = c.Article.FulltextUrl,
          SourceLinks = c.Article.SourceLinks
        })
        .ToListAsync();

    /// <summary>The categories in sort order.</summary>
    public static Task<List<Category>> LoadCategoriesAsync(ArticlesDbContext dbContext) =>
      dbContext.Categories.AsNoTracking().OrderBy(c => c.SortOrder).ToListAsync();

    /// <summary>Secondary-tag count per category code, over CB articles.</summary>
    public static async Task<Dictionary<string, int>> LoadSecondaryTagCountsAsync(ArticlesDbContext dbContext)
    {
      var rows = await dbContext.ArticleCategories
        .AsNoTracking()
        .Where(ac => ac.TagType == ArticleTagType.Secondary && ac.Article.Code.StartsWith(CaninePrefix))
        .GroupBy(ac => ac.Category.Code)
        .Select(g => new { Code = g.Key, Count = g.Count() })
        .ToListAsync();
      return rows.ToDictionary(r => r.Code.Trim(), r => r.Count);
    }

    /// <summary>Articles with no cohort, plus one per distinct cohort.</summary>
    public static int IndependentSources(IEnumerable<ArticleFact> articles)
    {
      var list = articles as IList<ArticleFact> ?? articles.ToList();
      return list.Count(a => string.IsNullOrEmpty(a.CohortId))
        + list.Where(a => !string.IsNullOrEmpty(a.CohortId)).Select(a => a.CohortId).Distinct().Count();
    }

    /// <summary>Article count per period band.</summary>
    public static List<int> PeriodCounts(IEnumerable<ArticleFact> articles)
    {
      var list = articles as IList<ArticleFact> ?? articles.ToList();
      return Periods.Select(p => list.Count(a => a.PubYear >= p.FromYear && a.PubYear <= p.ToYear)).ToList();
    }

    /// <summary>One topics-table row for a category.</summary>
    public static TopicRowViewModel TopicRow(Category category, IEnumerable<ArticleFact> canine,
      IReadOnlyDictionary<string, int> secondaryTags)
    {
      var code = category.Code.Trim();
      var articles = canine.Where(a => a.CategoryCode?.Trim() == code).ToList();
      return new TopicRowViewModel
      {
        Code = code,
        Label = category.Label ?? category.Name,
        Name = category.Name,
        Articles = articles.Count,
        IndependentSources = IndependentSources(articles),
        CohortArticles = articles.Count(a => !string.IsNullOrEmpty(a.CohortId)),
        Cohorts = articles.Where(a => !string.IsNullOrEmpty(a.CohortId)).Select(a => a.CohortId).Distinct().Count(),
        SecondaryTags = secondaryTags.TryGetValue(code, out var tags) ? tags : 0,
        PeriodCounts = PeriodCounts(articles),
        NotHighConfidence = articles.Count(a => !a.HighConfidence),
        AbstractOnly = articles.Count(a => a.AbstractOnly)
      };
    }

    /// <summary>Articles and independent sources per study type, in <see cref="ArticleClassification.StudyTypes"/> order.</summary>
    public static List<BreakdownRowViewModel> DesignRows(IEnumerable<ArticleFact> articles)
    {
      var list = articles as IList<ArticleFact> ?? articles.ToList();
      return ArticleClassification.StudyTypes
        .Select(type =>
        {
          var rows = list.Where(a => a.StudyType == type).ToList();
          return new BreakdownRowViewModel
          {
            Label = type,
            FilterValue = type,
            Articles = rows.Count,
            IndependentSources = IndependentSources(rows)
          };
        })
        .ToList();
    }

    /// <summary>The topic's sections from dbo.synthesis_section, in reading order.</summary>
    public static Task<List<SynthesisSection>> LoadSynthesisAsync(ArticlesDbContext dbContext, params string[] documentCodes) =>
      dbContext.SynthesisSections
        .AsNoTracking()
        .Where(s => documentCodes.Contains(s.DocumentCode))
        .OrderBy(s => s.DocumentCode).ThenBy(s => s.SectionOrder)
        .ToListAsync();

    public static SynthesisSectionViewModel ToViewModel(SynthesisSection section) =>
      new SynthesisSectionViewModel { Key = section.SectionKey, Heading = section.Heading, Body = section.Body };

    /// <summary>The source link of an article, as the Articles grid resolves it.</summary>
    public static string SourceUrl(ArticleFact article) =>
      ArticleSourceLink.Resolve(article.Doi, article.Pmid, article.SourceLinks, article.FulltextUrl);

    /// <summary>The median of a list, or null when it is empty.</summary>
    public static double? Median(IEnumerable<int> values)
    {
      var sorted = values.OrderBy(v => v).ToList();
      if (sorted.Count == 0)
      {
        return null;
      }
      int mid = sorted.Count / 2;
      return sorted.Count % 2 == 1 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2.0;
    }

    /// <summary>The latest load time of the given sections (UTC), or null when none are loaded.</summary>
    public static DateTime? LoadedAt(IEnumerable<SynthesisSection> sections) =>
      sections.Select(s => (DateTime?)DateTime.SpecifyKind(s.LoadedAt, DateTimeKind.Utc)).Max();
  }
}
