using Babesiosis.Core.Api.Review.Commands;
using Babesiosis.Core.Api.Review.ViewModels;
using Babesiosis.Core.ViewModels;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Review.Controllers
{
  /// <summary>
  /// Review list for the web application, in the standard
  /// <c>{ page, permissions }</c> envelope.
  ///
  /// Placeholder: the rows are hard-coded so the screen can be wired end to end.
  /// Phase two replaces them with a query and fills in the capability echo.
  /// </summary>
  public class GetReviewListController
  {
    public Task<ItemsViewModel<ReviewViewModel>> HandleCommand(Guid userId, GetReviewListCommand command)
    {
      var items = new List<ReviewViewModel>
      {
        new ReviewViewModel { Title = "Sample review 1", Status = "Open", UpdatedDate = DateTime.UtcNow.AddDays(-1) },
        new ReviewViewModel { Title = "Sample review 2", Status = "In progress", UpdatedDate = DateTime.UtcNow.AddDays(-3) },
        new ReviewViewModel { Title = "Sample review 3", Status = "Closed", UpdatedDate = DateTime.UtcNow.AddDays(-7) },
      };

      return Task.FromResult(new ItemsViewModel<ReviewViewModel>
      {
        Page = new PagedItemsViewModel<ReviewViewModel>
        {
          Items = items,
          Paging = new PagingViewModel(items.Count, 0, items.Count)
        }
      });
    }
  }
}
