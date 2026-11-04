using Babesiosis.Core.Models.Domain;
using System;

namespace Babesiosis.Core.ViewModels
{
    public class PagerViewModel
  {
    public PagerViewModel(int page, int pageSize, int pageRecordCount, int recordCount)
    {
      Start = recordCount == 0 ? 0 : Math.Max(0, (pageSize * (page - 1)) + 1);
      End = page == 1 ? pageRecordCount : (pageSize * (page - 1)) + pageRecordCount;
      Page = page;
      PageSize = pageSize;
      var pageCount = (double)recordCount / (double)pageSize;
      PageCount = recordCount == 0 ? 0 : Math.Max(1, (int)Math.Round(pageCount, MidpointRounding.AwayFromZero));
      PageRecordCount = pageRecordCount;
      RecordCount = recordCount;
    }

    public PagerViewModel(PagedResultBase result)
    {
      Start = result.RecordStart;
      End = result.RecordEnd;
      Page = result.Page;
      PageSize = result.PageSize;
      PageCount = result.PageCount;
      PageRecordCount = result.RecordCount;
      RecordCount = result.TotalRecordCount;
    }

    /// <summary>
    /// The start of the record count such as {1}-10 of 100
    /// </summary>
    public int Start { get; set; }
    /// <summary>
    /// The end of the record count such as 1-{10} of 100
    /// </summary>
    public int End { get; set; }

    /// <summary>
    /// Current page
    /// </summary>
    public int Page { get; set; }

    /// <summary>
    /// Number of records configured on a page
    /// </summary>
    public int PageSize { get; set; }

    /// <summary> 
    /// Total number of pages
    /// </summary>
    public int PageCount { get; set; }

    /// <summary>
    /// Actual number of records in page such as {10} of {100}
    /// </summary>
    public int PageRecordCount { get; set; }

    /// <summary>
    /// Total number of records in dataset such as 10 of {100}
    /// </summary>
    public int RecordCount { get; set; }
  }
}
