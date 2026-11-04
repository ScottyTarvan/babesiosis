using System;

namespace Babesiosis.Core.Permissions.Configs
{
  /// <summary>
  /// Permissions for the Teams area — roles, the permissions granted to a role,
  /// the members assigned to a role, users, and the roles assigned to a user.
  /// </summary>
  public static class TeamsPermissions
  {
    const string TEAMS = "teams";
    const string ROLE = "role";
    const string ROLE_PERMISSIONS = "role-permissions";
    const string ROLE_MEMBER = "role-member";
    const string USER = "user";
    const string USER_ROLE = "user-role";

    //************************************************
    //ROLE
    //************************************************
    public const string RoleReadId = "{4745FC12-14EA-44D4-8E47-E6A60D68A8C6}";
    public static PermissionItem RoleRead => new PermissionItem
    {
      Id = Guid.Parse(RoleReadId),
      Category = TEAMS,
      Group = ROLE,
      Action = PermissionAction.Read
    };

    public const string RoleAddId = "{03F87002-0A48-40E4-8CAE-3B03056BA5F9}";
    public static PermissionItem RoleAdd => new PermissionItem
    {
      Id = Guid.Parse(RoleAddId),
      Category = TEAMS,
      Group = ROLE,
      Action = PermissionAction.Add
    };

    public const string RoleEditId = "{7279F4D3-C4B9-483D-8F7F-3AD1855F247E}";
    public static PermissionItem RoleEdit => new PermissionItem
    {
      Id = Guid.Parse(RoleEditId),
      Category = TEAMS,
      Group = ROLE,
      Action = PermissionAction.Edit
    };

    public const string RoleDeleteId = "{72F5EF81-5AD2-452E-904E-484B010CD2DB}";
    public static PermissionItem RoleDelete => new PermissionItem
    {
      Id = Guid.Parse(RoleDeleteId),
      Category = TEAMS,
      Group = ROLE,
      Action = PermissionAction.Delete
    };

    // Gates exporting the roles grid. Export was ungated until now.
    public const string RoleDownloadId = "{D640586D-D628-41C5-B957-A360D39DAB40}";
    public static PermissionItem RoleDownload => new PermissionItem
    {
      Id = Guid.Parse(RoleDownloadId),
      Category = TEAMS,
      Group = ROLE,
      Action = PermissionAction.Download
    };

    //************************************************
    //ROLE PERMISSIONS
    //************************************************
    // Role permissions are not independently creatable or deletable — they are
    // edited in place on a role — so only Read and Edit exist here.
    public const string RolePermissionReadId = "{D08F9A20-3AE7-47AC-B83C-6DE1A6786CA7}";
    public static PermissionItem RolePermissionRead => new PermissionItem
    {
      Id = Guid.Parse(RolePermissionReadId),
      Category = TEAMS,
      Group = ROLE_PERMISSIONS,
      Action = PermissionAction.Read
    };

    public const string RolePermissionEditId = "{79E1D4E3-CFB9-4F25-9795-148CA90B5DBE}";
    public static PermissionItem RolePermissionEdit => new PermissionItem
    {
      Id = Guid.Parse(RolePermissionEditId),
      Category = TEAMS,
      Group = ROLE_PERMISSIONS,
      Action = PermissionAction.Edit
    };

    //************************************************
    //ROLE MEMBER
    //************************************************
    // Assigning and removing a member both count as Edit — the membership list
    // is a property of the role, not a record in its own right.
    public const string RoleMemberReadId = "{95D44E23-E196-4AF1-82EB-02F492C955C9}";
    public static PermissionItem RoleMemberRead => new PermissionItem
    {
      Id = Guid.Parse(RoleMemberReadId),
      Category = TEAMS,
      Group = ROLE_MEMBER,
      Action = PermissionAction.Read
    };

    public const string RoleMemberEditId = "{1694A095-47C0-4BEF-8CDE-3F9DCE728DE2}";
    public static PermissionItem RoleMemberEdit => new PermissionItem
    {
      Id = Guid.Parse(RoleMemberEditId),
      Category = TEAMS,
      Group = ROLE_MEMBER,
      Action = PermissionAction.Edit
    };

    //************************************************
    //USER
    //************************************************
    public const string UserReadId = "{A28F0E4A-1630-4AE6-8C77-E16A70DD8660}";
    public static PermissionItem UserRead => new PermissionItem
    {
      Id = Guid.Parse(UserReadId),
      Category = TEAMS,
      Group = USER,
      Action = PermissionAction.Read
    };

    public const string UserAddId = "{97DD0B39-79B7-4A47-A64C-0CF904482B90}";
    public static PermissionItem UserAdd => new PermissionItem
    {
      Id = Guid.Parse(UserAddId),
      Category = TEAMS,
      Group = USER,
      Action = PermissionAction.Add
    };

    public const string UserEditId = "{426AC349-F6F9-494D-8EB5-13778D9E2D60}";
    public static PermissionItem UserEdit => new PermissionItem
    {
      Id = Guid.Parse(UserEditId),
      Category = TEAMS,
      Group = USER,
      Action = PermissionAction.Edit
    };

    public const string UserDeleteId = "{5AEB3EF3-70D5-4BE8-99BB-E37F6008E858}";
    public static PermissionItem UserDelete => new PermissionItem
    {
      Id = Guid.Parse(UserDeleteId),
      Category = TEAMS,
      Group = USER,
      Action = PermissionAction.Delete
    };

    // Gates setting/clearing IsAdministrator on a user. This is asserted
    // conditionally inside the create/update controllers rather than declared
    // as a [RequiredPermission] attribute, because whether it applies depends
    // on the payload (is IsAdministrator being changed?), not on which
    // endpoint was called.
    public const string UserElevateId = "{ADDDEEE3-1787-4D47-B985-4588EDB36A67}";
    public static PermissionItem UserElevate => new PermissionItem
    {
      Id = Guid.Parse(UserElevateId),
      Category = TEAMS,
      Group = USER,
      Action = PermissionAction.Elevate
    };

    // Gates exporting the users grid. This carries user PII, so unlike most
    // grid exports it is called out on its own rather than folded into Read.
    public const string UserDownloadId = "{9AADA595-4E05-4B5B-9181-1A0E8908EC94}";
    public static PermissionItem UserDownload => new PermissionItem
    {
      Id = Guid.Parse(UserDownloadId),
      Category = TEAMS,
      Group = USER,
      Action = PermissionAction.Download
    };

    //************************************************
    //USER ROLE
    //************************************************
    public const string UserRoleReadId = "{A5FE8CC0-70B7-45B5-A2BC-3D2462CEDC11}";
    public static PermissionItem UserRoleRead => new PermissionItem
    {
      Id = Guid.Parse(UserRoleReadId),
      Category = TEAMS,
      Group = USER_ROLE,
      Action = PermissionAction.Read
    };

    public const string UserRoleEditId = "{98FA69C8-78D2-49FE-B910-72433A55B4D6}";
    public static PermissionItem UserRoleEdit => new PermissionItem
    {
      Id = Guid.Parse(UserRoleEditId),
      Category = TEAMS,
      Group = USER_ROLE,
      Action = PermissionAction.Edit
    };
  }
}
