using Babesiosis.Core.ViewModels;
using System;

namespace Babesiosis.Core.Api.Review.ViewModels
{
  /// <summary>One row of the Review list.</summary>
  public class ReviewViewModel : ViewModel
  {
    public string Title { get; set; }
    public string Status { get; set; }
    public DateTime UpdatedDate { get; set; }
  }
}
