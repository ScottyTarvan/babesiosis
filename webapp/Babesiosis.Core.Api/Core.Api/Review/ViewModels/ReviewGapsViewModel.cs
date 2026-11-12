using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>The Gaps and questions screen.</summary>
  public class ReviewGapsViewModel
  {
    /// <summary>The matrix columns, the study types in display order.</summary>
    public List<string> Designs { get; set; } = new List<string>();
    /// <summary>One row per category, most articles first.</summary>
    public List<GapRowViewModel> Rows { get; set; } = new List<GapRowViewModel>();
    public int CanineArticles { get; set; }
    public List<GapFigureViewModel> Figures { get; set; } = new List<GapFigureViewModel>();
    /// <summary>The numbered themes of CROSS.md, as written.</summary>
    public List<SynthesisSectionViewModel> Themes { get; set; } = new List<SynthesisSectionViewModel>();
    /// <summary>Q1–Q5 of QUESTIONS.md, as written.</summary>
    public List<SynthesisSectionViewModel> Questions { get; set; } = new List<SynthesisSectionViewModel>();
    /// <summary>UTC, when CROSS.md and QUESTIONS.md were loaded; null when they are not.</summary>
    public DateTime? SynthesisLoadedAt { get; set; }
  }

  /// <summary>One matrix row: a category's articles per study type.</summary>
  public class GapRowViewModel
  {
    public string Code { get; set; }
    public string Label { get; set; }
    public string Name { get; set; }
    /// <summary>Articles per study type, in the order of <see cref="ReviewGapsViewModel.Designs"/>.</summary>
    public List<int> Counts { get; set; } = new List<int>();
    public int Total { get; set; }
  }

  /// <summary>One computed gap figure: a number, what it counts, and a sentence of context.</summary>
  public class GapFigureViewModel
  {
    public string Key { get; set; }
    public string Value { get; set; }
    public string Title { get; set; }
    public string Text { get; set; }
  }
}
