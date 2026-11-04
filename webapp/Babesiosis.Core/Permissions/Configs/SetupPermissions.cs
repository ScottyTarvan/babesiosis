using System;

namespace Babesiosis.Core.Permissions.Configs
{
  /// <summary>
  /// Permissions for the Setup area — the screens that define the warehouse:
  /// linked services, datasets and their sub-resources, entity groups, event
  /// triggers, and the file upload/download drop-point definitions.
  ///
  /// The five dataset-type groups (entity, classification, data-table, lookup,
  /// reference) are declared per type because every dataset controller asserts
  /// per type; the dataset sub-resource groups (dataset-field, dataset-index,
  /// dataset-key, …) are shared across all five types, since a sub-resource is
  /// only reachable inside a dataset the caller already holds the type's Read on.
  ///
  /// Endpoints whose permission varies by dataset type cannot use
  /// <c>[RequiredPermission]</c> — attribute arguments are compile-time
  /// constants. They resolve through <c>DatasetPermissionItems</c> instead.
  /// </summary>
  public static class SetupPermissions
  {
    const string SETUP = "setup";
    const string LINKED_SERVICE = "linked-service";
    const string ENTITY = "entity";
    const string CLASSIFICATION = "classification";
    const string DATA_TABLE = "data-table";
    const string LOOKUP = "lookup";
    const string REFERENCE = "reference";
    const string DATASET_FIELD = "dataset-field";
    const string DATASET_INDEX = "dataset-index";
    const string DATASET_KEY = "dataset-key";
    const string DATASET_DEPLOYMENT = "dataset-deployment";
    const string DATASET_ASSET = "dataset-asset";
    const string DATASET_DIAGNOSTICS = "dataset-diagnostics";
    const string DATASET_EXPECTATION = "dataset-expectation";
    const string ENTITY_GROUP = "entity-group";
    const string ENTITY_GROUP_DESIGNER = "entity-group-designer";
    const string EVENT_TRIGGER = "event-trigger";
    const string EVENT_TRIGGER_PARAMETER = "event-trigger-parameter";
    const string FILE_UPLOAD = "file-upload";
    const string FILE_DOWNLOAD = "file-download";
    const string MAPPING = "mapping";

    //************************************************
    //LINKED SERVICE
    //************************************************
    // Testing a connection reads the stored configuration and mutates nothing,
    // so it is gated on Read rather than an action of its own.
    public const string LinkedServiceReadId = "{2CEE2909-5B90-4F3D-A4FA-DDE09F473F38}";
    public static PermissionItem LinkedServiceRead => new PermissionItem
    {
      Id = Guid.Parse(LinkedServiceReadId),
      Category = SETUP,
      Group = LINKED_SERVICE,
      Action = PermissionAction.Read
    };

    public const string LinkedServiceAddId = "{1018DB89-851A-43A8-943A-A5CF7B007309}";
    public static PermissionItem LinkedServiceAdd => new PermissionItem
    {
      Id = Guid.Parse(LinkedServiceAddId),
      Category = SETUP,
      Group = LINKED_SERVICE,
      Action = PermissionAction.Add
    };

    public const string LinkedServiceEditId = "{ACCE299C-21EA-4D1F-A64D-50929AE72A19}";
    public static PermissionItem LinkedServiceEdit => new PermissionItem
    {
      Id = Guid.Parse(LinkedServiceEditId),
      Category = SETUP,
      Group = LINKED_SERVICE,
      Action = PermissionAction.Edit
    };

    public const string LinkedServiceDeleteId = "{B9F37B33-300C-4D51-9925-981E4D5D470B}";
    public static PermissionItem LinkedServiceDelete => new PermissionItem
    {
      Id = Guid.Parse(LinkedServiceDeleteId),
      Category = SETUP,
      Group = LINKED_SERVICE,
      Action = PermissionAction.Delete
    };

    //************************************************
    //ENTITY
    //************************************************
    // The five dataset-type groups are deliberately separate. Every dataset
    // controller asserts per type today, so a single collapsed "dataset" group
    // would widen an existing lookup-only grant to all five types.
    // Read also opens the dataset hub: the legacy "-details:read" grant is
    // folded in, because nothing documents list-but-not-open.
    public const string EntityReadId = "{98C6E11F-910C-493E-8B19-F067DBEBC049}";
    public static PermissionItem EntityRead => new PermissionItem
    {
      Id = Guid.Parse(EntityReadId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Read
    };

    public const string EntityAddId = "{43B592B2-F83A-49E7-88B5-753ADF75FDAF}";
    public static PermissionItem EntityAdd => new PermissionItem
    {
      Id = Guid.Parse(EntityAddId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Add
    };

    public const string EntityEditId = "{7AF0B4F4-DF2F-4DD0-98C2-036473907288}";
    public static PermissionItem EntityEdit => new PermissionItem
    {
      Id = Guid.Parse(EntityEditId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Edit
    };

    public const string EntityDeleteId = "{6F0CAC9A-4424-4DF0-8205-3511EF6617A3}";
    public static PermissionItem EntityDelete => new PermissionItem
    {
      Id = Guid.Parse(EntityDeleteId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Delete
    };

    public const string EntityDeployId = "{EE1A0BBA-24A9-4564-8BA5-E6AC18B914DF}";
    public static PermissionItem EntityDeploy => new PermissionItem
    {
      Id = Guid.Parse(EntityDeployId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Deploy
    };

    public const string EntityLinkId = "{A38B08F1-26C0-4863-BCB9-3C1429C6BE1A}";
    public static PermissionItem EntityLink => new PermissionItem
    {
      Id = Guid.Parse(EntityLinkId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Link
    };

    public const string EntityUnlinkId = "{2DCC2C10-0FF1-414D-8125-FC1259BFE6CA}";
    public static PermissionItem EntityUnlink => new PermissionItem
    {
      Id = Guid.Parse(EntityUnlinkId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Unlink
    };

    public const string EntityDownloadId = "{C55E794A-4033-490C-9A3D-D2F721BD3F00}";
    public static PermissionItem EntityDownload => new PermissionItem
    {
      Id = Guid.Parse(EntityDownloadId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Download
    };

    public const string EntityUploadId = "{1C282F4F-D541-4707-AE33-11B442B52D5E}";
    public static PermissionItem EntityUpload => new PermissionItem
    {
      Id = Guid.Parse(EntityUploadId),
      Category = SETUP,
      Group = ENTITY,
      Action = PermissionAction.Upload
    };

    //************************************************
    //CLASSIFICATION
    //************************************************
    // Dataset type Attribute resolves here too. DatasetPermissionItems and the
    // legacy DatasetActionPermissions.GetSubject make the same collapse; there
    // is no attribute group.
    public const string ClassificationReadId = "{15606E12-1513-41BC-A644-ED04E640CC87}";
    public static PermissionItem ClassificationRead => new PermissionItem
    {
      Id = Guid.Parse(ClassificationReadId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Read
    };

    public const string ClassificationAddId = "{954ABF5C-9C1D-4B37-B364-77F2CBAAC46F}";
    public static PermissionItem ClassificationAdd => new PermissionItem
    {
      Id = Guid.Parse(ClassificationAddId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Add
    };

    public const string ClassificationEditId = "{C1646B61-9019-45DE-A1BE-EB9407865C26}";
    public static PermissionItem ClassificationEdit => new PermissionItem
    {
      Id = Guid.Parse(ClassificationEditId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Edit
    };

    public const string ClassificationDeleteId = "{74197A0E-0A3A-444B-BA24-22D68384C66E}";
    public static PermissionItem ClassificationDelete => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDeleteId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Delete
    };

    public const string ClassificationDeployId = "{C9DE2BF1-2EE8-40CB-A7F1-709380D5E869}";
    public static PermissionItem ClassificationDeploy => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDeployId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Deploy
    };

    public const string ClassificationLinkId = "{B14E9127-483F-4EBE-843A-517554DA3CF2}";
    public static PermissionItem ClassificationLink => new PermissionItem
    {
      Id = Guid.Parse(ClassificationLinkId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Link
    };

    public const string ClassificationUnlinkId = "{C851BD6E-967C-4574-8ED5-52119CD8CF0E}";
    public static PermissionItem ClassificationUnlink => new PermissionItem
    {
      Id = Guid.Parse(ClassificationUnlinkId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Unlink
    };

    public const string ClassificationDownloadId = "{18B023AA-9125-4BF0-9C34-2DB421810A6E}";
    public static PermissionItem ClassificationDownload => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDownloadId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Download
    };

    public const string ClassificationUploadId = "{008DC3E5-DBD8-4C9C-963F-1B0BAD242A39}";
    public static PermissionItem ClassificationUpload => new PermissionItem
    {
      Id = Guid.Parse(ClassificationUploadId),
      Category = SETUP,
      Group = CLASSIFICATION,
      Action = PermissionAction.Upload
    };

    //************************************************
    //DATA TABLE
    //************************************************
    // Dataset type Fact. The group carries the user-facing name, not the enum
    // name, and is kebab-cased "data-table".
    public const string DataTableReadId = "{0F6663F1-42D5-4C0B-8F11-C2D5BF3EDC2B}";
    public static PermissionItem DataTableRead => new PermissionItem
    {
      Id = Guid.Parse(DataTableReadId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Read
    };

    public const string DataTableAddId = "{BB4EBFB8-1EEB-4474-80B9-0D026EA1D5E7}";
    public static PermissionItem DataTableAdd => new PermissionItem
    {
      Id = Guid.Parse(DataTableAddId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Add
    };

    public const string DataTableEditId = "{4ABCF4E3-89F8-4331-94A1-CEB3B7092E63}";
    public static PermissionItem DataTableEdit => new PermissionItem
    {
      Id = Guid.Parse(DataTableEditId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Edit
    };

    public const string DataTableDeleteId = "{03F5DD01-7A3E-4B49-8441-514BC4B6E03A}";
    public static PermissionItem DataTableDelete => new PermissionItem
    {
      Id = Guid.Parse(DataTableDeleteId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Delete
    };

    public const string DataTableDeployId = "{86F34EFD-8BDF-403D-8307-31467F1B6756}";
    public static PermissionItem DataTableDeploy => new PermissionItem
    {
      Id = Guid.Parse(DataTableDeployId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Deploy
    };

    public const string DataTableLinkId = "{3E54B016-B51B-4144-AF75-711E7C45E3BE}";
    public static PermissionItem DataTableLink => new PermissionItem
    {
      Id = Guid.Parse(DataTableLinkId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Link
    };

    public const string DataTableUnlinkId = "{74F4686C-EDDE-48B8-9D47-45C27B9C869B}";
    public static PermissionItem DataTableUnlink => new PermissionItem
    {
      Id = Guid.Parse(DataTableUnlinkId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Unlink
    };

    public const string DataTableDownloadId = "{E507083A-C42E-4FB4-9BB2-130EBEB3FA43}";
    public static PermissionItem DataTableDownload => new PermissionItem
    {
      Id = Guid.Parse(DataTableDownloadId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Download
    };

    public const string DataTableUploadId = "{B996126F-CC42-43CC-A06E-3C549C7986D7}";
    public static PermissionItem DataTableUpload => new PermissionItem
    {
      Id = Guid.Parse(DataTableUploadId),
      Category = SETUP,
      Group = DATA_TABLE,
      Action = PermissionAction.Upload
    };

    //************************************************
    //LOOKUP
    //************************************************
    public const string LookupReadId = "{39D4D6B1-E9D1-4A36-A8FC-E55672CE527F}";
    public static PermissionItem LookupRead => new PermissionItem
    {
      Id = Guid.Parse(LookupReadId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Read
    };

    public const string LookupAddId = "{AE816179-FD67-43CE-AC17-B66FA417FD6F}";
    public static PermissionItem LookupAdd => new PermissionItem
    {
      Id = Guid.Parse(LookupAddId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Add
    };

    public const string LookupEditId = "{E86EDB3F-07A3-49F9-8299-E61D7D119106}";
    public static PermissionItem LookupEdit => new PermissionItem
    {
      Id = Guid.Parse(LookupEditId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Edit
    };

    public const string LookupDeleteId = "{1D2C1906-9377-43EE-90AB-AE6ED47A8CC9}";
    public static PermissionItem LookupDelete => new PermissionItem
    {
      Id = Guid.Parse(LookupDeleteId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Delete
    };

    public const string LookupDeployId = "{4C93F39C-8BFA-40FE-81C9-45A30A3EA058}";
    public static PermissionItem LookupDeploy => new PermissionItem
    {
      Id = Guid.Parse(LookupDeployId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Deploy
    };

    public const string LookupLinkId = "{A5D72B04-2292-4ECD-95F4-F5F6D2162219}";
    public static PermissionItem LookupLink => new PermissionItem
    {
      Id = Guid.Parse(LookupLinkId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Link
    };

    public const string LookupUnlinkId = "{15EC6B99-A4A1-47CC-BE9E-454B5AEE73D0}";
    public static PermissionItem LookupUnlink => new PermissionItem
    {
      Id = Guid.Parse(LookupUnlinkId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Unlink
    };

    public const string LookupDownloadId = "{D748A74E-E34C-4910-8425-DA146B7C8420}";
    public static PermissionItem LookupDownload => new PermissionItem
    {
      Id = Guid.Parse(LookupDownloadId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Download
    };

    public const string LookupUploadId = "{4C727079-99F6-4DED-8DCF-109A505B0332}";
    public static PermissionItem LookupUpload => new PermissionItem
    {
      Id = Guid.Parse(LookupUploadId),
      Category = SETUP,
      Group = LOOKUP,
      Action = PermissionAction.Upload
    };

    //************************************************
    //REFERENCE
    //************************************************
    // Reference is the LOCKED type. Its datasets are the platform's own lists — Country,
    // Currency, Calendar — and the rule (user directive 2026-08-27) is that no user creates,
    // edits or removes one from the dataset screens at all. Only three authorities remain, and
    // each has exactly one live consumer:
    //
    //   Read     — listing and opening a reference dataset.
    //   Deploy   — Import Reference Lists on the linked services screen, which is now the ONLY
    //              path that brings a reference dataset into existence, and the redeploy that
    //              refreshes its schema and seed for a system upgrade.
    //   Delete   — Remove Reference Lists on that same screen, the sanctioned undo of an import.
    //              It is NOT the dataset list's Delete, which ReferenceDatasetGuards refuses
    //              outright; the linked services screen is the only place the question "is
    //              anything using this yet?" can actually be answered.
    //   Download — exporting the definition, a read.
    //
    // Add, Edit, Link, Unlink and Upload are RETIRED: see the block below.
    public const string ReferenceReadId = "{FBFDA73F-AEF6-4CDC-BA43-95FBA152119A}";
    public static PermissionItem ReferenceRead => new PermissionItem
    {
      Id = Guid.Parse(ReferenceReadId),
      Category = SETUP,
      Group = REFERENCE,
      Action = PermissionAction.Read
    };

    public const string ReferenceDeleteId = "{663675D7-2012-4CBA-ABA8-6158D7E7FEB9}";
    public static PermissionItem ReferenceDelete => new PermissionItem
    {
      Id = Guid.Parse(ReferenceDeleteId),
      Category = SETUP,
      Group = REFERENCE,
      Action = PermissionAction.Delete
    };

    public const string ReferenceDeployId = "{A2C6C147-1540-4EEA-9103-9799F28661AC}";
    public static PermissionItem ReferenceDeploy => new PermissionItem
    {
      Id = Guid.Parse(ReferenceDeployId),
      Category = SETUP,
      Group = REFERENCE,
      Action = PermissionAction.Deploy
    };

    public const string ReferenceDownloadId = "{C06B9405-765E-4A6D-B24C-34ABC9DEC601}";
    public static PermissionItem ReferenceDownload => new PermissionItem
    {
      Id = Guid.Parse(ReferenceDownloadId),
      Category = SETUP,
      Group = REFERENCE,
      Action = PermissionAction.Download
    };

    //------------------------------------------------------------------------
    // RETIRED REFERENCE PERMISSIONS — declared nowhere, grantable nowhere.
    //------------------------------------------------------------------------
    // These five were real items until 2026-08-27. They are gone from the catalogue because
    // PermissionsConfigService reflects over public static PermissionItem PROPERTIES, so deleting
    // the property is what removes the checkbox from the role matrix. A capability flag alone
    // would have left five grants an administrator could tick and that would then do nothing —
    // the same reasoning ManagePermissionItems already applies to reference Add and Delete.
    //
    // The ids survive as consts for two reasons: SQL 0049 deletes the grant rows 0019 and 0048
    // created against them, and a future item must never reuse one of these GUIDs — a recycled
    // id would silently inherit every role that still carries the orphaned grant.
    //
    // DatasetPermissionItems.Supports(Reference, ...) is the code-side answer for these, and it
    // answers false before DatasetPermissionItems.For is ever asked to resolve them.
    public const string RetiredReferenceAddId = "{A1161364-53FA-41D0-9BD0-891BEEFE437D}";
    public const string RetiredReferenceEditId = "{86F19EB1-41B7-49A3-9FE5-632D28543657}";
    public const string RetiredReferenceLinkId = "{DC7A8874-4ACF-4ED5-88ED-2A43437193C5}";
    public const string RetiredReferenceUnlinkId = "{3AA458F5-DFB2-41BB-8E1C-6C15AC8453D4}";
    public const string RetiredReferenceUploadId = "{CC2FD0E6-8830-4C6F-96D4-9CA3C41C54EA}";

    //************************************************
    //DATASET FIELD
    //************************************************
    // The dataset sub-resource groups are type-agnostic on purpose:
    // dataset-field:edit covers fields on all five dataset types. A
    // sub-resource is only reachable inside a dataset the caller already holds
    // the type's Read on, so the type group still bounds the scope. Thirty
    // per-type sub-resource groups would make the role matrix unusable.
    // Covers both the Fields tab and the System Fields tab.
    public const string DatasetFieldReadId = "{7656E3A5-B8F3-4412-8A8F-5FC06478795A}";
    public static PermissionItem DatasetFieldRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetFieldReadId),
      Category = SETUP,
      Group = DATASET_FIELD,
      Action = PermissionAction.Read
    };

    public const string DatasetFieldAddId = "{6B11D5D9-6CE8-44E7-9538-B5B873CAECE1}";
    public static PermissionItem DatasetFieldAdd => new PermissionItem
    {
      Id = Guid.Parse(DatasetFieldAddId),
      Category = SETUP,
      Group = DATASET_FIELD,
      Action = PermissionAction.Add
    };

    public const string DatasetFieldEditId = "{330B853E-7CD4-4BE4-96EF-4A47E81B2936}";
    public static PermissionItem DatasetFieldEdit => new PermissionItem
    {
      Id = Guid.Parse(DatasetFieldEditId),
      Category = SETUP,
      Group = DATASET_FIELD,
      Action = PermissionAction.Edit
    };

    public const string DatasetFieldDeleteId = "{DB672AD6-1EB0-43E1-BCDE-9F1909370B26}";
    public static PermissionItem DatasetFieldDelete => new PermissionItem
    {
      Id = Guid.Parse(DatasetFieldDeleteId),
      Category = SETUP,
      Group = DATASET_FIELD,
      Action = PermissionAction.Delete
    };

    //************************************************
    //DATASET INDEX
    //************************************************
    // Index fields are part of the index, not a record of their own, so editing
    // and reordering them is Edit on the index.
    public const string DatasetIndexReadId = "{26EFD6F6-4DE0-41DF-8AEF-343F0B682799}";
    public static PermissionItem DatasetIndexRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetIndexReadId),
      Category = SETUP,
      Group = DATASET_INDEX,
      Action = PermissionAction.Read
    };

    public const string DatasetIndexAddId = "{4AF485DD-B6DE-4C28-B5E4-608323D8B6A4}";
    public static PermissionItem DatasetIndexAdd => new PermissionItem
    {
      Id = Guid.Parse(DatasetIndexAddId),
      Category = SETUP,
      Group = DATASET_INDEX,
      Action = PermissionAction.Add
    };

    public const string DatasetIndexEditId = "{C0AC7B62-C31B-4F6D-9285-6D71C085D3E7}";
    public static PermissionItem DatasetIndexEdit => new PermissionItem
    {
      Id = Guid.Parse(DatasetIndexEditId),
      Category = SETUP,
      Group = DATASET_INDEX,
      Action = PermissionAction.Edit
    };

    public const string DatasetIndexDeleteId = "{74665D39-8071-4336-BE8A-12F8B312EFC5}";
    public static PermissionItem DatasetIndexDelete => new PermissionItem
    {
      Id = Guid.Parse(DatasetIndexDeleteId),
      Category = SETUP,
      Group = DATASET_INDEX,
      Action = PermissionAction.Delete
    };

    //************************************************
    //DATASET KEY
    //************************************************
    // Keys are edited in place on the dataset and are never independently added
    // or deleted, so only Read and Edit exist here.
    public const string DatasetKeyReadId = "{77A4894E-F08F-4D43-A6EB-8F5656BEC09A}";
    public static PermissionItem DatasetKeyRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetKeyReadId),
      Category = SETUP,
      Group = DATASET_KEY,
      Action = PermissionAction.Read
    };

    public const string DatasetKeyEditId = "{1BF90550-DBFA-4209-9CE1-8EA4932883EE}";
    public static PermissionItem DatasetKeyEdit => new PermissionItem
    {
      Id = Guid.Parse(DatasetKeyEditId),
      Category = SETUP,
      Group = DATASET_KEY,
      Action = PermissionAction.Edit
    };

    //************************************************
    //DATASET DEPLOYMENT
    //************************************************
    // Read covers the deployment log, run history and task logs; Download covers
    // their text and Excel exports; Delete covers purging a settled run out of
    // the history. Run control (approve, decline, resume,
    // abandon) is NOT an action here — it resolves from the run's own
    // DeploymentAction onto the dataset type group's Deploy/Delete/Unlink/Link
    // through DatasetPermissionItems.ForRun.
    public const string DatasetDeploymentReadId = "{659DC46C-A1C5-41F5-9F7F-21CE2CBD8A7F}";
    public static PermissionItem DatasetDeploymentRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetDeploymentReadId),
      Category = SETUP,
      Group = DATASET_DEPLOYMENT,
      Action = PermissionAction.Read
    };

    public const string DatasetDeploymentDownloadId = "{902EF6A3-3502-4A25-B6D6-4684B1172F90}";
    public static PermissionItem DatasetDeploymentDownload => new PermissionItem
    {
      Id = Guid.Parse(DatasetDeploymentDownloadId),
      Category = SETUP,
      Group = DATASET_DEPLOYMENT,
      Action = PermissionAction.Download
    };

    // Purging one run out of the history: the run header, its plan steps and
    // their logs, and the legacy DeploymentLog/DeploymentTaskLog rows raised
    // alongside it. Its OWN item rather than the dataset type group's Delete,
    // which destroys a dataset — erasing the audit of a delete and performing
    // one are different authorities, and a role that may tear a dataset down
    // must not silently also be able to erase the record that it did.
    public const string DatasetDeploymentDeleteId = "{7C4E0B36-9A21-4D8E-B0F5-3E6C1A97D452}";
    public static PermissionItem DatasetDeploymentDelete => new PermissionItem
    {
      Id = Guid.Parse(DatasetDeploymentDeleteId),
      Category = SETUP,
      Group = DATASET_DEPLOYMENT,
      Action = PermissionAction.Delete
    };

    //************************************************
    //DATASET ASSET
    //************************************************
    // Generated DDL and scripts are disclosure only; there is no write path, so
    // Read is the only action.
    public const string DatasetAssetReadId = "{B815F540-AB03-4894-A7D2-DE8618A41F80}";
    public static PermissionItem DatasetAssetRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetAssetReadId),
      Category = SETUP,
      Group = DATASET_ASSET,
      Action = PermissionAction.Read
    };

    //************************************************
    //DATASET DIAGNOSTICS
    //************************************************
    // The Validations and Diagnostics tabs are both read-only quality reports.
    public const string DatasetDiagnosticsReadId = "{FD83C538-B17A-40F9-A600-181600163EB4}";
    public static PermissionItem DatasetDiagnosticsRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetDiagnosticsReadId),
      Category = SETUP,
      Group = DATASET_DIAGNOSTICS,
      Action = PermissionAction.Read
    };

    /// <summary>
    /// Accepting the database as a dataset's recorded state — the exit from a deployment blocked on
    /// schema drift.
    /// <para>
    /// Its own item rather than riding on the Read above, because it is the one thing this feature
    /// does that is not reading: it rewrites the baseline a deployment plan is built from, and a
    /// wrong baseline yields a wrong plan. The controller demands the dataset type's DEPLOY
    /// authority as well — reconciliation changes what a deployment will do, so being allowed to
    /// deploy is the floor, and this item narrows who may do it from there.
    /// </para>
    /// </summary>
    public const string DatasetDiagnosticsReconcileId = "{3C7E1B94-6A2D-4E58-9F03-5D81C6A47B12}";
    public static PermissionItem DatasetDiagnosticsReconcile => new PermissionItem
    {
      Id = Guid.Parse(DatasetDiagnosticsReconcileId),
      Category = SETUP,
      Group = DATASET_DIAGNOSTICS,
      Action = PermissionAction.Edit
    };

    /// <summary>
    /// Running a NON-DESTRUCTIVE remediation from a Diagnostics row — stamping the deployer's
    /// identity markers onto a table or an index, re-checking or re-enabling a foreign key,
    /// restoring a column the design describes and the database has lost.
    /// <para>
    /// Its own item rather than riding on <see cref="DatasetDiagnosticsReconcile"/>, because it is
    /// the first thing this screen does that writes to the CUSTOMER'S database rather than to
    /// <c>meta</c>. Reconcile can only ever produce a wrong row in the metadata; this produces a
    /// statement against a live table. The controller demands the dataset type's DEPLOY authority
    /// as well — that is the floor for anything that changes what a deployment will find — and this
    /// item narrows who may do it from there.
    /// </para>
    /// <para>
    /// Action <see cref="PermissionAction.Run"/>, not Edit: Edit in this group already means
    /// "reconcile", and a second Edit row would be indistinguishable from it on the role screen.
    /// Run is also the honest verb — a remediation executes a deployment step.
    /// </para>
    /// <para>
    /// GUID fixed by SQL script <c>0039_DiagnosticsRemediation_PermissionGrant.sql</c>, which grants
    /// it to every role already holding <see cref="DatasetDiagnosticsReconcile"/>. It must never
    /// change: the grant rows key off it.
    /// </para>
    /// </summary>
    public const string DatasetDiagnosticsRemediateId = "{277D3920-04B8-4AF8-804B-03319AA66A95}";
    public static PermissionItem DatasetDiagnosticsRemediate => new PermissionItem
    {
      Id = Guid.Parse(DatasetDiagnosticsRemediateId),
      Category = SETUP,
      Group = DATASET_DIAGNOSTICS,
      Action = PermissionAction.Run
    };

    /// <summary>
    /// Running a DESTRUCTIVE remediation from a Diagnostics row — dropping a column, an index or a
    /// foreign key out of the customer's database.
    /// <para>
    /// Deliberately separate from <see cref="DatasetDiagnosticsRemediate"/>, and separate from the
    /// dataset type's own delete authority. Deleting a DATASET is a decision about something FDM
    /// built and can rebuild; dropping one column out of a live table is a decision about the
    /// customer's data, taken from a diagnostics screen, with no plan preview and no approval gate.
    /// Those are not the same grant, and rolling them together would mean anyone who can remediate
    /// at all can destroy.
    /// </para>
    /// <para>
    /// Declared here even though nothing asserts it yet: the four destructive row actions are a
    /// later work package, and the grant script that seeds this id ships now. An item whose id is
    /// already in the database and not yet in the code would be a grant nothing can consume.
    /// </para>
    /// <para>
    /// GUID fixed by SQL script <c>0039_DiagnosticsRemediation_PermissionGrant.sql</c>. It must
    /// never change.
    /// </para>
    /// </summary>
    public const string DatasetDiagnosticsRemediateDestructiveId = "{4E6E557B-C847-4F51-8A50-CCCCF12F7A83}";
    public static PermissionItem DatasetDiagnosticsRemediateDestructive => new PermissionItem
    {
      Id = Guid.Parse(DatasetDiagnosticsRemediateDestructiveId),
      Category = SETUP,
      Group = DATASET_DIAGNOSTICS,
      Action = PermissionAction.Delete
    };

    //************************************************
    //ENTITY GROUP
    //************************************************
    // The entity group record itself — the list and its add/edit dialog.
    public const string EntityGroupReadId = "{2D1658B5-D1CC-4ACD-9395-0987700D6496}";
    public static PermissionItem EntityGroupRead => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupReadId),
      Category = SETUP,
      Group = ENTITY_GROUP,
      Action = PermissionAction.Read
    };

    public const string EntityGroupAddId = "{D4665E39-9DF1-43A0-826F-02347D640DCE}";
    public static PermissionItem EntityGroupAdd => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupAddId),
      Category = SETUP,
      Group = ENTITY_GROUP,
      Action = PermissionAction.Add
    };

    public const string EntityGroupEditId = "{D4EA73E0-5492-43E8-B0F9-F8F4A04C21D7}";
    public static PermissionItem EntityGroupEdit => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupEditId),
      Category = SETUP,
      Group = ENTITY_GROUP,
      Action = PermissionAction.Edit
    };

    public const string EntityGroupDeleteId = "{CCFA05AC-D5F6-4509-8FDC-B8A69F8343AF}";
    public static PermissionItem EntityGroupDelete => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupDeleteId),
      Category = SETUP,
      Group = ENTITY_GROUP,
      Action = PermissionAction.Delete
    };

    //************************************************
    //ENTITY GROUP DESIGNER
    //************************************************
    // Deliberately distinct from entity-group: holding one does not imply the
    // other. The designer has no Add or Delete of its own — the entity group is
    // the record; the designer only edits and deploys it.
    public const string EntityGroupDesignerReadId = "{A46B278A-B4F3-4362-B6BE-D40C75F0DB01}";
    public static PermissionItem EntityGroupDesignerRead => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupDesignerReadId),
      Category = SETUP,
      Group = ENTITY_GROUP_DESIGNER,
      Action = PermissionAction.Read
    };

    public const string EntityGroupDesignerEditId = "{AA7888C8-0C12-49ED-BDC4-F091AFB4D7C2}";
    public static PermissionItem EntityGroupDesignerEdit => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupDesignerEditId),
      Category = SETUP,
      Group = ENTITY_GROUP_DESIGNER,
      Action = PermissionAction.Edit
    };

    public const string EntityGroupDesignerDeployId = "{F4EF3A26-D982-4667-829B-7CCD5174BFAB}";
    public static PermissionItem EntityGroupDesignerDeploy => new PermissionItem
    {
      Id = Guid.Parse(EntityGroupDesignerDeployId),
      Category = SETUP,
      Group = ENTITY_GROUP_DESIGNER,
      Action = PermissionAction.Deploy
    };

    //************************************************
    //EVENT TRIGGER
    //************************************************
    // The UI calls these Activators; the legacy subject is setup-activator.
    public const string EventTriggerReadId = "{8569F782-1D49-4F9B-946B-C857FEC1CD15}";
    public static PermissionItem EventTriggerRead => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerReadId),
      Category = SETUP,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Read
    };

    public const string EventTriggerAddId = "{2B58E2A4-298F-41C6-86C7-96E203B3F802}";
    public static PermissionItem EventTriggerAdd => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerAddId),
      Category = SETUP,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Add
    };

    public const string EventTriggerEditId = "{38E37BAF-13B0-40B8-B32A-0AF75EEDC48C}";
    public static PermissionItem EventTriggerEdit => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerEditId),
      Category = SETUP,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Edit
    };

    public const string EventTriggerDeleteId = "{D73CEFC6-10F0-4D10-A43C-0E7716D5474B}";
    public static PermissionItem EventTriggerDelete => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerDeleteId),
      Category = SETUP,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Delete
    };

    //************************************************
    //EVENT TRIGGER PARAMETER
    //************************************************
    // Reordering a parameter is Edit — the order is a property of the parameter,
    // not a record of its own.
    public const string EventTriggerParameterReadId = "{58B17ECC-6D5F-4DD5-B343-8362521C802B}";
    public static PermissionItem EventTriggerParameterRead => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerParameterReadId),
      Category = SETUP,
      Group = EVENT_TRIGGER_PARAMETER,
      Action = PermissionAction.Read
    };

    public const string EventTriggerParameterAddId = "{5BB4B1D0-D560-4C90-BA4C-4756C71D613D}";
    public static PermissionItem EventTriggerParameterAdd => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerParameterAddId),
      Category = SETUP,
      Group = EVENT_TRIGGER_PARAMETER,
      Action = PermissionAction.Add
    };

    public const string EventTriggerParameterEditId = "{C77842DE-99FA-482C-9CBD-0F65920CE88C}";
    public static PermissionItem EventTriggerParameterEdit => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerParameterEditId),
      Category = SETUP,
      Group = EVENT_TRIGGER_PARAMETER,
      Action = PermissionAction.Edit
    };

    public const string EventTriggerParameterDeleteId = "{E73C1E80-1CE8-4B57-997D-54A666F3C8C7}";
    public static PermissionItem EventTriggerParameterDelete => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerParameterDeleteId),
      Category = SETUP,
      Group = EVENT_TRIGGER_PARAMETER,
      Action = PermissionAction.Delete
    };

    //************************************************
    //FILE UPLOAD
    //************************************************
    // Drop-point definitions, not the files themselves. Dropping a file is a
    // Manage action — see ManagePermissions.FileUploadUpload.
    public const string FileUploadReadId = "{DBF44561-6B23-4124-B2A7-400F5CBF92B6}";
    public static PermissionItem FileUploadRead => new PermissionItem
    {
      Id = Guid.Parse(FileUploadReadId),
      Category = SETUP,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Read
    };

    public const string FileUploadAddId = "{E8DE169A-1BEF-4293-B7F5-4A905EC32769}";
    public static PermissionItem FileUploadAdd => new PermissionItem
    {
      Id = Guid.Parse(FileUploadAddId),
      Category = SETUP,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Add
    };

    public const string FileUploadEditId = "{BF58CF39-72C6-499F-9372-9C89CFCE9646}";
    public static PermissionItem FileUploadEdit => new PermissionItem
    {
      Id = Guid.Parse(FileUploadEditId),
      Category = SETUP,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Edit
    };

    public const string FileUploadDeleteId = "{FB6ABC7B-BAF1-4CFF-B16B-DFE8F95EC415}";
    public static PermissionItem FileUploadDelete => new PermissionItem
    {
      Id = Guid.Parse(FileUploadDeleteId),
      Category = SETUP,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Delete
    };

    //************************************************
    //FILE DOWNLOAD
    //************************************************
    // Pick-up-point definitions, not the files themselves. Collecting a file is
    // a Manage action — see ManagePermissions.FileDownloadDownload.
    public const string FileDownloadReadId = "{BA8305C0-A372-4024-9EB3-8B6679C1B058}";
    public static PermissionItem FileDownloadRead => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadReadId),
      Category = SETUP,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Read
    };

    public const string FileDownloadAddId = "{A5E8B522-5DDD-460B-AB87-B850EB1EEC58}";
    public static PermissionItem FileDownloadAdd => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadAddId),
      Category = SETUP,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Add
    };

    public const string FileDownloadEditId = "{489F082C-6111-4A82-AFF1-A6C5F91EB122}";
    public static PermissionItem FileDownloadEdit => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadEditId),
      Category = SETUP,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Edit
    };

    public const string FileDownloadDeleteId = "{33B54CF4-ECE8-432E-95BB-F8BC744F311B}";
    public static PermissionItem FileDownloadDelete => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadDeleteId),
      Category = SETUP,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Delete
    };

    //************************************************
    //MAPPING
    //************************************************
    // The Mappings screens under Setup — binding an incoming source file's
    // fields to a deployed dataset's fields. ACTIVATION asserts Edit rather
    // than carrying a permission of its own: activating a mapping is a state
    // change on a record the caller can already edit, not a distinct
    // capability. There is no Deploy action here — unlike the dataset type
    // groups above, this feature only ever defines a binding; it moves no
    // data, so nothing in this group ever reaches a customer database.
    public const string MappingReadId = "{9805ED2F-6BAC-45C7-8B36-A4267709A64A}";
    public static PermissionItem MappingRead => new PermissionItem
    {
      Id = Guid.Parse(MappingReadId),
      Category = SETUP,
      Group = MAPPING,
      Action = PermissionAction.Read
    };

    public const string MappingAddId = "{D6F9AE73-1809-4BEA-AF01-77440E2796A3}";
    public static PermissionItem MappingAdd => new PermissionItem
    {
      Id = Guid.Parse(MappingAddId),
      Category = SETUP,
      Group = MAPPING,
      Action = PermissionAction.Add
    };

    public const string MappingEditId = "{256BC106-4510-47DA-8951-E5493E7E71DD}";
    public static PermissionItem MappingEdit => new PermissionItem
    {
      Id = Guid.Parse(MappingEditId),
      Category = SETUP,
      Group = MAPPING,
      Action = PermissionAction.Edit
    };

    public const string MappingDeleteId = "{FFF65DA7-ACFE-40DA-90AE-923047EB2C66}";
    public static PermissionItem MappingDelete => new PermissionItem
    {
      Id = Guid.Parse(MappingDeleteId),
      Category = SETUP,
      Group = MAPPING,
      Action = PermissionAction.Delete
    };

    //************************************************
    //DATASET EXPECTATION
    //************************************************
    public const string DatasetExpectationReadId = "{45EEB208-9E83-48B1-934B-52A09DCEA8AC}";
    public static PermissionItem DatasetExpectationRead => new PermissionItem
    {
      Id = Guid.Parse(DatasetExpectationReadId),
      Category = SETUP,
      Group = DATASET_EXPECTATION,
      Action = PermissionAction.Read
    };

    public const string DatasetExpectationAddId = "{4A07D032-3B66-411C-AFB9-7C4BF4C83588}";
    public static PermissionItem DatasetExpectationAdd => new PermissionItem
    {
      Id = Guid.Parse(DatasetExpectationAddId),
      Category = SETUP,
      Group = DATASET_EXPECTATION,
      Action = PermissionAction.Add
    };

    public const string DatasetExpectationEditId = "{1524F85A-02F2-44DB-981F-E484E6533C66}";
    public static PermissionItem DatasetExpectationEdit => new PermissionItem
    {
      Id = Guid.Parse(DatasetExpectationEditId),
      Category = SETUP,
      Group = DATASET_EXPECTATION,
      Action = PermissionAction.Edit
    };

    public const string DatasetExpectationDeleteId = "{8717A08C-81C8-4B7A-90E6-5E793B802E12}";
    public static PermissionItem DatasetExpectationDelete => new PermissionItem
    {
      Id = Guid.Parse(DatasetExpectationDeleteId),
      Category = SETUP,
      Group = DATASET_EXPECTATION,
      Action = PermissionAction.Delete
    };

    public const string DatasetExpectationAcknowledgeId = "{9C6A0F1E-2B7D-4E5A-8F3C-1D6E4A9B5C2F}";
    public static PermissionItem DatasetExpectationAcknowledge => new PermissionItem
    {
      Id = Guid.Parse(DatasetExpectationAcknowledgeId),
      Category = SETUP,
      Group = DATASET_EXPECTATION,
      Action = PermissionAction.Approve
    };

    //************************************************
    //DATA HEALTH COLLECTOR SETTINGS
    //************************************************
    // Settings and run status for the health collector: viewing the current
    // configuration and monitoring status (Read), or changing metric group
    // schedules, enabling/pausing groups, modifying dataset inclusion, and
    // selecting columns for statistics (Edit).
    const string DATA_HEALTH_COLLECTOR_SETTINGS = "data-health-collector-settings";
    const string DATA_HEALTH_DASHBOARD = "data-health-dashboard";

    public const string DataHealthCollectorSettingsReadId = "{138C261A-F153-4A03-8240-B3BF7A451377}";
    public static PermissionItem DataHealthCollectorSettingsRead => new PermissionItem
    {
      Id = Guid.Parse(DataHealthCollectorSettingsReadId),
      Category = SETUP,
      Group = DATA_HEALTH_COLLECTOR_SETTINGS,
      Action = PermissionAction.Read
    };

    public const string DataHealthCollectorSettingsEditId = "{8584B221-3CB5-4D3E-9C9A-FE0FDBC0F56D}";
    public static PermissionItem DataHealthCollectorSettingsEdit => new PermissionItem
    {
      Id = Guid.Parse(DataHealthCollectorSettingsEditId),
      Category = SETUP,
      Group = DATA_HEALTH_COLLECTOR_SETTINGS,
      Action = PermissionAction.Edit
    };

    //************************************************
    //DATA HEALTH DASHBOARD
    //************************************************
    // Opening /health, viewing the system dashboard, and viewing the user's
    // own personal dashboards (Read). Edit enters edit mode and changes the
    // dashboard layout (Edit implies Read). Add and Delete are not declared
    // in this build (Planned). No role grants until explicitly granted (only
    // admins under the single admin rule until that point).
    public const string DataHealthDashboardReadId = "{33BC722C-EF68-45B5-AC2D-AB549A224027}";
    public static PermissionItem DataHealthDashboardRead => new PermissionItem
    {
      Id = Guid.Parse(DataHealthDashboardReadId),
      Category = SETUP,
      Group = DATA_HEALTH_DASHBOARD,
      Action = PermissionAction.Read
    };

    public const string DataHealthDashboardEditId = "{F9B27061-DD58-4BF6-933B-EF7301B865E6}";
    public static PermissionItem DataHealthDashboardEdit => new PermissionItem
    {
      Id = Guid.Parse(DataHealthDashboardEditId),
      Category = SETUP,
      Group = DATA_HEALTH_DASHBOARD,
      Action = PermissionAction.Edit
    };
  }
}
