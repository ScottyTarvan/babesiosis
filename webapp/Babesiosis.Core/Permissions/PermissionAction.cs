using System;

namespace Babesiosis.Core.Permissions
{
  /// <summary>
  /// The verb half of a permission triple. Values describe *user intent*, not
  /// the HTTP verb — a PATCH that publishes a dataset is <see cref="Deploy"/>,
  /// not <see cref="Edit"/>.
  ///
  /// Values are persisted only indirectly (a grant stores the permission's
  /// GUID, never this enum), so renumbering would not corrupt data — but the
  /// name is rendered by the role-permissions UI, so treat additions as a
  /// front-end contract change.
  /// </summary>
  public enum PermissionAction
  {
    None = 0,
    Add = 1,
    Read = 2,
    Edit = 3,
    Delete = 4,
    Deploy = 5,
    Download = 6,
    Upload = 7,
    Run = 8,
    // Link adopts an existing physical table into FDM and Unlink severs that
    // adoption without dropping the table. Neither folds into Add/Delete: the
    // legacy grants they replace were seeded from deploy holders, not create
    // holders, and unlink is deliberately a smaller blast radius than delete.
    Link = 9,
    Unlink = 10,
    // Approve is a sign-off on a rendered document; Distribute releases it
    // outside the system. Neither is Edit (nothing on the record is
    // authored) nor Run (nothing is executed).
    Approve = 11,
    Distribute = 12,
    // Elevate grants a user the blanket IsAdministrator flag. It is not Edit:
    // UserPermissionItemsService short-circuits on user.IsAdministrator, so
    // this one flag confers every permission in both models at once. A user
    // trusted to correct someone's phone number should not thereby be
    // trusted to make them an administrator.
    Elevate = 13
  }
}
