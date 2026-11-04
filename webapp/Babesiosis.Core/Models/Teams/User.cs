using System;
using System.Collections.Generic;
using Babesiosis.Core.Models.Domain;

namespace Babesiosis.Core.Models.Teams
{
  public class User : InstanceModel
  {
    public byte[] RowVersion { get; set; }
    public DateTime CreatedDate { get; set; }
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string Email { get; set; }
    public string Password { get; set; }
    public string IV { get; set; }
    public string Salt { get; set; }
    public string MobileNumberCode { get; set; }
    public string MobileNumber { get; set; }
    public string LandlineNumberCode { get; set; }
    public string LandlineNumber { get; set; }
    public bool IsAdministrator { get; set; }
    public bool IsSuperAdministrator { get; set; }
    public string AvatarUrl { get; set; }
    public bool IsDeleted { get; set; }

    public List<UserRole> UserRoles { get; set; } = new();
    public override string ToString()
    {
      return $"{FirstName} {LastName}";
    }
  }
}
