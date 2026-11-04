using System.Collections.Generic;

namespace Babesiosis.Core.ViewModels
{
  /// <summary>
  /// One page of rows plus its paging metadata.
  /// Serializes as <c>{ items, paging }</c>, which is what the new web
  /// application's <c>PagedResult&lt;T&gt;</c> binds to.
  /// </summary>
  public class PagedItemsViewModel<T>
  {
    public IEnumerable<T> Items { get; set; } = new List<T>();
    public PagingViewModel Paging { get; set; } = new PagingViewModel();
  }

  /// <summary>
  /// The standard list-endpoint envelope for the new web application:
  /// a page of rows plus the capability dictionary the screen gates its
  /// actions on.
  ///
  /// The capability echo is the prototype's pattern — the client never sees
  /// permission GUIDs, only the answers to the questions this screen asks
  /// ("canAdd", "canEdit", …), computed server-side from the caller's grants.
  /// </summary>
  public class ItemsViewModel<T>
  {
    public PagedItemsViewModel<T> Page { get; set; } = new PagedItemsViewModel<T>();
    public Dictionary<string, bool> Permissions { get; set; } = new Dictionary<string, bool>();
  }
}
