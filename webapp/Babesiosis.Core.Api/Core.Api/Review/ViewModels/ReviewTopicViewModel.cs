using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>One topic (category) page: its figures, its narrative synthesis and its articles.</summary>
  public class ReviewTopicViewModel
  {
    public TopicRowViewModel Topic { get; set; }
    /// <summary>Every canine article, the base of the topic's share.</summary>
    public int CanineArticles { get; set; }
    public List<PeriodViewModel> Periods { get; set; } = new List<PeriodViewModel>();
    public List<BreakdownRowViewModel> Designs { get; set; } = new List<BreakdownRowViewModel>();
    /// <summary>The synthesis sections as written, in reading order; empty when the file is not loaded.</summary>
    public List<SynthesisSectionViewModel> Synthesis { get; set; } = new List<SynthesisSectionViewModel>();
    /// <summary>UTC, when the synthesis was loaded; null when it is not.</summary>
    public DateTime? SynthesisLoadedAt { get; set; }
    /// <summary>The topic's articles, newest first.</summary>
    public List<TopicArticleViewModel> Articles { get; set; } = new List<TopicArticleViewModel>();
    /// <summary>Every category, for the topic switcher.</summary>
    public List<TopicLinkViewModel> Topics { get; set; } = new List<TopicLinkViewModel>();
  }

  /// <summary>One article in a topic's list.</summary>
  public class TopicArticleViewModel
  {
    public string Code { get; set; }
    public int? Year { get; set; }
    public string Title { get; set; }
    public string StudyType { get; set; }
    public int? InfectedDogs { get; set; }
    public int? Controls { get; set; }
    public string Species { get; set; }
    public string Finding { get; set; }
    public bool AbstractOnly { get; set; }
    public bool HighConfidence { get; set; }
    /// <summary>Publisher, PubMed or a landing page; null when none is known.</summary>
    public string SourceUrl { get; set; }
  }

  /// <summary>One entry of the topic switcher.</summary>
  public class TopicLinkViewModel
  {
    public string Code { get; set; }
    public string Label { get; set; }
    public string Name { get; set; }
    public int Articles { get; set; }
  }
}
