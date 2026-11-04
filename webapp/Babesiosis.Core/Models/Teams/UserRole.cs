using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;

namespace Babesiosis.Core.Models.Teams
{
  public class UserRole
  {
    public int UserId { get; set; }
    public int RoleId { get; set; }

    public User User { get; set; }
    public Role Role { get; set; }

    public class Comparer : IEqualityComparer<UserRole>
    {
      public bool Equals([AllowNull] UserRole x, [AllowNull] UserRole y)
      {
        return x.RoleId.Equals(y.RoleId) && x.UserId.Equals(y.UserId);
      }

      public int GetHashCode([DisallowNull] UserRole obj)
      {
        int hash = 37;
        hash = hash * 23 + obj.UserId.GetHashCode();
        hash = hash * 23 + obj.RoleId.GetHashCode();
        return hash;
      }
    }
  }
}
