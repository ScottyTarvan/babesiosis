using System.Collections.Generic;

namespace Babesiosis.Core.ViewModels
{
  public class UserViewModel : ViewModel
  {
    public string FirstName { get; set; }
    public string LastName { get; set; }
    public string Email { get; set; }
    public string Password { get; set; }
    public string MobileNumberCode { get; set; }
    public string MobileNumber { get; set; }
    public string LandlineNumberCode { get; set; }
    public string LandlineNumber { get; set; }
    public bool IsAdministrator { get; set; }

    /// <summary>
    /// Surfaced so the new web application's SuperAdminRoleGuard and shell nav
    /// can gate the super-admin-only areas. AutoMapper picks it up by
    /// convention from <c>User.IsSuperAdministrator</c>.
    /// </summary>
    public bool IsSuperAdministrator { get; set; }

    public bool IsDeleted { get; set; }
    public UserPermissionsViewModel Permissions { get; set; }
  }
}
