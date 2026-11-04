using System;

namespace Babesiosis.Core.ViewModels
{
  /// <summary>
  /// Zero-based paging envelope used by the new web application's data grids.
  ///
  /// Distinct from <see cref="PagerViewModel"/>, which is one-based and speaks
  /// in record ranges ("1-10 of 100") — that one stays as-is because every
  /// legacy screen binds to it.
  /// </summary>
  public class PagingViewModel
  {
    public int TotalCount { get; set; }
    public int PageIndex { get; set; }
    public int PageSize { get; set; }
    public int TotalPages { get; set; }
    public bool HasPreviousPage => PageIndex > 0;
    public bool HasNextPage => PageIndex + 1 < TotalPages;

    public PagingViewModel() { }

    public PagingViewModel(int totalCount, int skip, int take)
    {
      TotalCount = totalCount;
      PageSize = take <= 0 ? totalCount : take;
      PageIndex = PageSize <= 0 ? 0 : skip / PageSize;
      TotalPages = PageSize <= 0 ? 0 : (int)Math.Ceiling(totalCount / (double)PageSize);
    }
  }
}
