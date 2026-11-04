using Babesiosis.Core.Models.Domain;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Teams
{
    public class UserNotification : IdModel
  {
    public int UserId { get; set; }
    public NotificationType Type { get; set; }
    public User User { get; set; }
    public new class Comparer : IEqualityComparer<UserNotification>
    {
      public bool Equals(UserNotification x, UserNotification y)
      {
        return x.UserId == y.UserId && x.Type == y.Type;
      }

      public int GetHashCode(UserNotification obj)
      {
        return obj.Id.GetHashCode();
      }
    }
  }
}
