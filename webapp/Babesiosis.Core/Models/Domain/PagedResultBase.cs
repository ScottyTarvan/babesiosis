using System;

namespace Babesiosis.Core.Models.Domain
{
  public abstract class PagedResultBase
  {
    /// <summary>
    /// Current page
    /// </summary>
    public int Page { get; set; }

    /// <summary>
    /// Number of records on a page
    /// </summary>
    public int PageSize { get; set; }

    /// <summary>
    /// Total number of pages
    /// </summary>
    public int PageCount { get; set; }

    /// <summary>
    /// The start of the record count such as {1}-10 of 100
    /// </summary>
    public int RecordStart => Math.Max(1, PageSize * (Page - 1) + 1);

    /// <summary>
    /// The end of the record count such as 1-{10} of 100
    /// </summary>
    public int RecordEnd => Math.Min(TotalRecordCount, PageSize * Page);

    /// <summary>
    /// Actual number of records in page such as {10} of {100}
    /// </summary>
    public int RecordCount { get; set; }

    /// <summary>
    /// Total number of records in data set such as 10 of {100}
    /// </summary>
    public int TotalRecordCount { get; set; }
  }
}
