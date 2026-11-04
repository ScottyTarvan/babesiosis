using System.Collections.Generic;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>
  /// Article counts as a category-by-year matrix. <see cref="Years"/> is the
  /// x-axis, every year from the earliest to the latest with no gaps; each
  /// category row holds one count per year, in the same order.
  /// </summary>
  public class CategoryYearCountsViewModel
  {
    public List<int> Years { get; set; } = new List<int>();
    public List<CategoryYearCountsRowViewModel> Categories { get; set; } = new List<CategoryYearCountsRowViewModel>();
  }

  /// <summary>One category row of the matrix, in category sort order.</summary>
  public class CategoryYearCountsRowViewModel
  {
    public string Code { get; set; }
    public string Name { get; set; }
    /// <summary>Short display name, e.g. "Renal". Null when the category has none.</summary>
    public string Label { get; set; }
    /// <summary>One count per entry of <see cref="CategoryYearCountsViewModel.Years"/>; zero when the category has no articles that year.</summary>
    public List<int> Counts { get; set; } = new List<int>();
  }
}
