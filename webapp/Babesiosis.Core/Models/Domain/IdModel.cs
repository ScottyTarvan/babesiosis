using System.Collections.Generic;

namespace Babesiosis.Core.Models.Domain
{
  public abstract class IdModel 
  {
    public int Id { get; set; }

    public class IdModelComparer : IEqualityComparer<IdModel>
    {
      public bool Equals(IdModel x, IdModel y)
      {
        return x.Id == y.Id;
      }

      public int GetHashCode(IdModel obj)
      {
        return obj.Id.GetHashCode();
      }
    }
  }
}
