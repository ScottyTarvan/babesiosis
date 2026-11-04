using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>
  /// Canine (CB) article counts per publication year, grouped into blocks (study type,
  /// Babesia species). Within a block each article sits in exactly one row.
  /// </summary>
  public class EvidenceProfileViewModel
  {
    /// <summary>CB articles counted (every block sums to this).</summary>
    public int ArticleCount { get; set; }
    /// <summary>The fixed year axis, oldest first; every row's Counts lines up with it.</summary>
    public List<int> Years { get; set; } = new List<int>();
    public List<EvidenceProfileBlockViewModel> Blocks { get; set; } = new List<EvidenceProfileBlockViewModel>();
  }

  /// <summary>One way of slicing the articles, e.g. "By study type".</summary>
  public class EvidenceProfileBlockViewModel
  {
    public string Title { get; set; }
    public List<EvidenceProfileRowViewModel> Rows { get; set; } = new List<EvidenceProfileRowViewModel>();
  }

  /// <summary>One row: its label, its article total and the raw count per year (zero-filled).</summary>
  public class EvidenceProfileRowViewModel
  {
    public string Label { get; set; }
    public int Total { get; set; }
    public List<int> Counts { get; set; } = new List<int>();
  }
}
