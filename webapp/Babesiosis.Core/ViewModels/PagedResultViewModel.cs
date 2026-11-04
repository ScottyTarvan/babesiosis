using Babesiosis.Core.Models.Domain;
using System.Collections.Generic;

namespace Babesiosis.Core.ViewModels
{
  public class PagedResultViewModel<T> : PagedResultBase
  {
    /// <summary>
    /// The paged entities
    /// </summary>
    public IEnumerable<T> Results { get; set; } = new List<T>();
  }
}
