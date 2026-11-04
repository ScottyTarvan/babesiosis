using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Domain
{
  public abstract class InstanceModel : IdModel
  {
    public Guid InstanceId { get; set; } = Guid.NewGuid();

    public class InstanceModelComparer : IEqualityComparer<InstanceModel>
    {
      public bool Equals(InstanceModel x, InstanceModel y)
      {
        return x.InstanceId == y.InstanceId;
      }

      public int GetHashCode(InstanceModel obj)
      {
        return obj.InstanceId.GetHashCode();
      }
    }
  }
}
