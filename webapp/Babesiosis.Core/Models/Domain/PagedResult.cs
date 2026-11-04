using System.Collections.Generic;

namespace Babesiosis.Core.Models.Domain
{
  public class PagedResult<TEntity> : PagedResultBase where TEntity : class
  {

    /// <summary>
    /// The paged entities
    /// </summary>
    public IEnumerable<TEntity> Results { get; set; } = new List<TEntity>();
  }
}
