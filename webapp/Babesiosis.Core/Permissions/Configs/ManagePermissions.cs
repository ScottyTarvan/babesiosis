using System;

namespace Babesiosis.Core.Permissions.Configs
{
  /// <summary>
  /// Permissions for the Manage area — the screens that operate a deployed
  /// warehouse rather than define it: the dataset data grids, activator runs,
  /// file drops and file pick-ups.
  ///
  /// Dataset types are declared per type for the same reason Setup declares them
  /// per type — the legacy grant is per type and collapsing would widen it. The
  /// <c>&lt;type&gt;</c> groups gate the /manage/:type list; the
  /// <c>&lt;type&gt;-data</c> groups gate the data grid inside one dataset.
  ///
  /// The reference groups are narrower than the rest, on purpose. A reference
  /// dataset is one of the platform-owned lists (Country, Currency), whose row
  /// set is seeded and whose ids are stored in customer data — so the screen
  /// corrects a row, it does not add or remove one. <c>reference-data</c>
  /// therefore declares Read, Edit and Download and NO Add or Delete, and the
  /// two write controllers refuse the type outright rather than resolving an
  /// item that does not exist.
  ///
  /// Endpoints whose permission varies by dataset type cannot use
  /// <c>[RequiredPermission]</c>; they resolve through
  /// <c>ManagePermissionItems</c> instead.
  /// </summary>
  public static class ManagePermissions
  {
    const string MANAGE = "manage";
    const string ENTITY = "entity";
    const string ENTITY_DATA = "entity-data";
    const string CLASSIFICATION = "classification";
    const string CLASSIFICATION_DATA = "classification-data";
    const string DATA_TABLE = "data-table";
    const string DATA_TABLE_DATA = "data-table-data";
    const string LOOKUP = "lookup";
    const string LOOKUP_DATA = "lookup-data";
    const string REFERENCE = "reference";
    const string REFERENCE_DATA = "reference-data";
    const string EVENT_TRIGGER = "event-trigger";
    const string FILE_UPLOAD = "file-upload";
    const string FILE_DOWNLOAD = "file-download";
    const string ENTITY_DATA_AUDIT = "entity-data-audit";
    const string ATTRIBUTE_DATA_AUDIT = "attribute-data-audit";
    const string CLASSIFICATION_DATA_AUDIT = "classification-data-audit";
    const string DATA_TABLE_DATA_AUDIT = "data-table-data-audit";
    const string LOOKUP_DATA_AUDIT = "lookup-data-audit";

    //************************************************
    //ENTITY
    //************************************************
    // The <type> groups gate the /manage/:type list; the <type>-data groups gate
    // the data grid inside one dataset. Dataset type Attribute resolves to the
    // classification groups and Fact to the data-table groups, exactly as in
    // Setup — see ManagePermissionItems.
    public const string EntityReadId = "{DF367EC0-A59E-4C7D-8EA9-147BC901F42E}";
    public static PermissionItem EntityRead => new PermissionItem
    {
      Id = Guid.Parse(EntityReadId),
      Category = MANAGE,
      Group = ENTITY,
      Action = PermissionAction.Read
    };

    //************************************************
    //ENTITY DATA
    //************************************************
    // No Delete: a delete path exists only for data tables and lookups, and the
    // manage data grid suppresses the action for the other types.
    public const string EntityDataReadId = "{89C5C428-501E-426A-B2E9-D91053118789}";
    public static PermissionItem EntityDataRead => new PermissionItem
    {
      Id = Guid.Parse(EntityDataReadId),
      Category = MANAGE,
      Group = ENTITY_DATA,
      Action = PermissionAction.Read
    };

    public const string EntityDataAddId = "{21BCC9BE-E55B-45C4-AC6A-F088D639CB12}";
    public static PermissionItem EntityDataAdd => new PermissionItem
    {
      Id = Guid.Parse(EntityDataAddId),
      Category = MANAGE,
      Group = ENTITY_DATA,
      Action = PermissionAction.Add
    };

    public const string EntityDataEditId = "{F0E9F687-06F9-4F63-93B8-0E0EA62E9F56}";
    public static PermissionItem EntityDataEdit => new PermissionItem
    {
      Id = Guid.Parse(EntityDataEditId),
      Category = MANAGE,
      Group = ENTITY_DATA,
      Action = PermissionAction.Edit
    };

    public const string EntityDataDownloadId = "{159DB045-D408-45BC-A4FB-D43F5CF0E149}";
    public static PermissionItem EntityDataDownload => new PermissionItem
    {
      Id = Guid.Parse(EntityDataDownloadId),
      Category = MANAGE,
      Group = ENTITY_DATA,
      Action = PermissionAction.Download
    };

    //************************************************
    //CLASSIFICATION
    //************************************************
    // Dataset type Attribute resolves here too.
    public const string ClassificationReadId = "{E841D46B-A2E2-4358-A688-052C6591EC7C}";
    public static PermissionItem ClassificationRead => new PermissionItem
    {
      Id = Guid.Parse(ClassificationReadId),
      Category = MANAGE,
      Group = CLASSIFICATION,
      Action = PermissionAction.Read
    };

    //************************************************
    //CLASSIFICATION DATA
    //************************************************
    // No Delete, for the same reason as entity-data.
    public const string ClassificationDataReadId = "{7FEE9CED-E05E-46C7-BE6B-120B72A86C1B}";
    public static PermissionItem ClassificationDataRead => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDataReadId),
      Category = MANAGE,
      Group = CLASSIFICATION_DATA,
      Action = PermissionAction.Read
    };

    public const string ClassificationDataAddId = "{D41B492E-D18E-4F70-8BE0-D34727C62D51}";
    public static PermissionItem ClassificationDataAdd => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDataAddId),
      Category = MANAGE,
      Group = CLASSIFICATION_DATA,
      Action = PermissionAction.Add
    };

    public const string ClassificationDataEditId = "{CE8959A1-4134-4D82-8F56-F4B72F5513C4}";
    public static PermissionItem ClassificationDataEdit => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDataEditId),
      Category = MANAGE,
      Group = CLASSIFICATION_DATA,
      Action = PermissionAction.Edit
    };

    public const string ClassificationDataDownloadId = "{59ED75E9-8614-415F-B4E4-D3EA62F83964}";
    public static PermissionItem ClassificationDataDownload => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDataDownloadId),
      Category = MANAGE,
      Group = CLASSIFICATION_DATA,
      Action = PermissionAction.Download
    };

    //************************************************
    //DATA TABLE
    //************************************************
    // Dataset type Fact.
    public const string DataTableReadId = "{3ADF36DB-1CB2-4188-A50E-A80C59A00BE8}";
    public static PermissionItem DataTableRead => new PermissionItem
    {
      Id = Guid.Parse(DataTableReadId),
      Category = MANAGE,
      Group = DATA_TABLE,
      Action = PermissionAction.Read
    };

    //************************************************
    //DATA TABLE DATA
    //************************************************
    public const string DataTableDataReadId = "{4E55AA23-645E-444E-B466-061E01337671}";
    public static PermissionItem DataTableDataRead => new PermissionItem
    {
      Id = Guid.Parse(DataTableDataReadId),
      Category = MANAGE,
      Group = DATA_TABLE_DATA,
      Action = PermissionAction.Read
    };

    public const string DataTableDataAddId = "{946402B7-124C-4E6D-BA4D-943E7F54F84A}";
    public static PermissionItem DataTableDataAdd => new PermissionItem
    {
      Id = Guid.Parse(DataTableDataAddId),
      Category = MANAGE,
      Group = DATA_TABLE_DATA,
      Action = PermissionAction.Add
    };

    public const string DataTableDataEditId = "{8D762F5F-96B3-4D5E-8D53-3174BC85139E}";
    public static PermissionItem DataTableDataEdit => new PermissionItem
    {
      Id = Guid.Parse(DataTableDataEditId),
      Category = MANAGE,
      Group = DATA_TABLE_DATA,
      Action = PermissionAction.Edit
    };

    public const string DataTableDataDeleteId = "{63FA68E2-BFD2-44BA-9AD8-B7F125663804}";
    public static PermissionItem DataTableDataDelete => new PermissionItem
    {
      Id = Guid.Parse(DataTableDataDeleteId),
      Category = MANAGE,
      Group = DATA_TABLE_DATA,
      Action = PermissionAction.Delete
    };

    public const string DataTableDataDownloadId = "{AD7C97B3-F061-415E-AD6A-B16362A064B2}";
    public static PermissionItem DataTableDataDownload => new PermissionItem
    {
      Id = Guid.Parse(DataTableDataDownloadId),
      Category = MANAGE,
      Group = DATA_TABLE_DATA,
      Action = PermissionAction.Download
    };

    //************************************************
    //LOOKUP
    //************************************************
    public const string LookupReadId = "{2284CF0D-07D5-40C4-9BF1-40907F35F42C}";
    public static PermissionItem LookupRead => new PermissionItem
    {
      Id = Guid.Parse(LookupReadId),
      Category = MANAGE,
      Group = LOOKUP,
      Action = PermissionAction.Read
    };

    //************************************************
    //LOOKUP DATA
    //************************************************
    public const string LookupDataReadId = "{A2EAA292-AD82-4595-87FE-C076782CC5E8}";
    public static PermissionItem LookupDataRead => new PermissionItem
    {
      Id = Guid.Parse(LookupDataReadId),
      Category = MANAGE,
      Group = LOOKUP_DATA,
      Action = PermissionAction.Read
    };

    public const string LookupDataAddId = "{61DCF38A-DBCE-4BB6-85F6-DE3C917556E0}";
    public static PermissionItem LookupDataAdd => new PermissionItem
    {
      Id = Guid.Parse(LookupDataAddId),
      Category = MANAGE,
      Group = LOOKUP_DATA,
      Action = PermissionAction.Add
    };

    public const string LookupDataEditId = "{85E10DC8-F9DE-4200-9BB2-EC1B27201519}";
    public static PermissionItem LookupDataEdit => new PermissionItem
    {
      Id = Guid.Parse(LookupDataEditId),
      Category = MANAGE,
      Group = LOOKUP_DATA,
      Action = PermissionAction.Edit
    };

    public const string LookupDataDeleteId = "{5A3FE5F9-6BD7-4C93-9C3C-518BA12FA7FF}";
    public static PermissionItem LookupDataDelete => new PermissionItem
    {
      Id = Guid.Parse(LookupDataDeleteId),
      Category = MANAGE,
      Group = LOOKUP_DATA,
      Action = PermissionAction.Delete
    };

    public const string LookupDataDownloadId = "{681E9926-7012-4D4B-932D-C954ED5F4A23}";
    public static PermissionItem LookupDataDownload => new PermissionItem
    {
      Id = Guid.Parse(LookupDataDownloadId),
      Category = MANAGE,
      Group = LOOKUP_DATA,
      Action = PermissionAction.Download
    };

    //************************************************
    //REFERENCE
    //************************************************
    // Dataset type Reference — the platform-owned lists. The group name matches
    // the Setup group of the same name, as every other type here does.
    public const string ReferenceReadId = "{6A1D5F2C-38B4-4E77-9C0A-2F5E8B41D963}";
    public static PermissionItem ReferenceRead => new PermissionItem
    {
      Id = Guid.Parse(ReferenceReadId),
      Category = MANAGE,
      Group = REFERENCE,
      Action = PermissionAction.Read
    };

    //************************************************
    //REFERENCE DATA
    //************************************************
    // No Add, no Edit and no Delete — the reference lists are READ ONLY as of the 2026-08-27
    // lockdown. Reading and exporting rows is all this group grants; the rows themselves change
    // only by redeploying the list, which reseeds it from the platform template.
    //
    // Edit was a real item for two days (0048, the /manage/references edit-only screen) and is
    // retired below rather than kept-but-inert, for the same reason the Setup ones are: a
    // grantable checkbox that does nothing is worse than no checkbox.
    public const string ReferenceDataReadId = "{C4B8E017-9D26-42A1-8F5B-73E0A1C6DD48}";
    public static PermissionItem ReferenceDataRead => new PermissionItem
    {
      Id = Guid.Parse(ReferenceDataReadId),
      Category = MANAGE,
      Group = REFERENCE_DATA,
      Action = PermissionAction.Read
    };

    // RETIRED 2026-08-27. Id kept so SQL 0049 can delete the grants 0048 created against it, and
    // so no future item reuses the GUID. ManagePermissionItems.SupportsEdit is the code answer.
    public const string RetiredReferenceDataEditId = "{2E9F73A5-6C10-4B8D-A47E-D5813F02B6C7}";

    public const string ReferenceDataDownloadId = "{8F04C1B6-27DE-4A93-B1E5-90C7A6482F31}";
    public static PermissionItem ReferenceDataDownload => new PermissionItem
    {
      Id = Guid.Parse(ReferenceDataDownloadId),
      Category = MANAGE,
      Group = REFERENCE_DATA,
      Action = PermissionAction.Download
    };

    //************************************************
    //EVENT TRIGGER
    //************************************************
    // Running an activator is Run; defining one is a Setup action — see
    // SetupPermissions.EventTrigger*. The UI calls these Activators.
    public const string EventTriggerReadId = "{740F3E75-CF61-44AB-A00A-6524C16F99A9}";
    public static PermissionItem EventTriggerRead => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerReadId),
      Category = MANAGE,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Read
    };

    public const string EventTriggerRunId = "{9FCD9FA7-F7CD-4248-94B0-E55F06EB7EC5}";
    public static PermissionItem EventTriggerRun => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerRunId),
      Category = MANAGE,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Run
    };

    // Gates exporting the activators grid. Export was ungated until now.
    public const string EventTriggerDownloadId = "{082C3E1A-DE67-412C-8C2B-AFB48FA6E3A9}";
    public static PermissionItem EventTriggerDownload => new PermissionItem
    {
      Id = Guid.Parse(EventTriggerDownloadId),
      Category = MANAGE,
      Group = EVENT_TRIGGER,
      Action = PermissionAction.Download
    };

    //************************************************
    //FILE UPLOAD
    //************************************************
    // Upload gates dropping a file into an existing drop point; the drop point
    // itself is defined under Setup — see SetupPermissions.FileUpload*.
    public const string FileUploadReadId = "{B65C0CDE-44D9-49D0-B73C-B5C313EBD430}";
    public static PermissionItem FileUploadRead => new PermissionItem
    {
      Id = Guid.Parse(FileUploadReadId),
      Category = MANAGE,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Read
    };

    public const string FileUploadUploadId = "{CE45D59F-09F9-4DE0-974B-E7F22A16BDC7}";
    public static PermissionItem FileUploadUpload => new PermissionItem
    {
      Id = Guid.Parse(FileUploadUploadId),
      Category = MANAGE,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Upload
    };

    // Removing a file already in a drop point, from the upload dialog's browser.
    // Its own grant rather than riding on Upload: a write can be redone, a
    // delete cannot.
    public const string FileUploadDeleteId = "{5E0B7A3C-2D41-4C8E-9F6A-B1D83C7E4A92}";
    public static PermissionItem FileUploadDelete => new PermissionItem
    {
      Id = Guid.Parse(FileUploadDeleteId),
      Category = MANAGE,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Delete
    };

    // Gates exporting the file-upload (drop point) grid. Export was ungated
    // until now.
    public const string FileUploadDownloadId = "{AD7C9778-EF72-4A9A-924C-715C57DE9C58}";
    public static PermissionItem FileUploadDownload => new PermissionItem
    {
      Id = Guid.Parse(FileUploadDownloadId),
      Category = MANAGE,
      Group = FILE_UPLOAD,
      Action = PermissionAction.Download
    };

    //************************************************
    //FILE DOWNLOAD
    //************************************************
    // Download gates collecting a file from an existing pick-up point; the pick-up
    // point itself is defined under Setup — see SetupPermissions.FileDownload*.
    public const string FileDownloadReadId = "{D379E904-6404-4DAE-A392-21B9CE8EEC9C}";
    public static PermissionItem FileDownloadRead => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadReadId),
      Category = MANAGE,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Read
    };

    public const string FileDownloadDownloadId = "{61810A52-C11E-41EA-883A-1FFCA473177C}";
    public static PermissionItem FileDownloadDownload => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadDownloadId),
      Category = MANAGE,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Download
    };

    // FileDownloadExport gates exporting the GRID of pick-up points to a
    // spreadsheet — a different capability from FileDownloadDownload, which
    // gates collecting a FILE from one pick-up point. Deliberately not named
    // FileDownloadDownload2 or similar: Export vs Download in the name is the
    // whole point, so the two are never confused at a glance.
    public const string FileDownloadExportId = "{6BF19294-9A42-456D-BA4B-CF7A4C11B80F}";
    public static PermissionItem FileDownloadExport => new PermissionItem
    {
      Id = Guid.Parse(FileDownloadExportId),
      Category = MANAGE,
      Group = FILE_DOWNLOAD,
      Action = PermissionAction.Download
    };

    //************************************************
    //ENTITY DATA AUDIT
    //************************************************
    // Viewing the audit trail of an Entity dataset. A separate grant, never the
    // entity-data Read: holding the data grant gives no access to its audit.
    public const string EntityDataAuditReadId = "{CC93F113-31F7-4B2F-B93C-0371FFA76F86}";
    public static PermissionItem EntityDataAuditRead => new PermissionItem
    {
      Id = Guid.Parse(EntityDataAuditReadId),
      Category = MANAGE,
      Group = ENTITY_DATA_AUDIT,
      Action = PermissionAction.Read
    };

    //************************************************
    //ATTRIBUTE DATA AUDIT
    //************************************************
    // Attribute has its own audit group, unlike its data grants, which share
    // Classification's group.
    public const string AttributeDataAuditReadId = "{ED7F6077-7A80-4AEC-8CE1-7CC646CDC65D}";
    public static PermissionItem AttributeDataAuditRead => new PermissionItem
    {
      Id = Guid.Parse(AttributeDataAuditReadId),
      Category = MANAGE,
      Group = ATTRIBUTE_DATA_AUDIT,
      Action = PermissionAction.Read
    };

    //************************************************
    //CLASSIFICATION DATA AUDIT
    //************************************************
    public const string ClassificationDataAuditReadId = "{B39D48A4-DDAD-4D31-8F7F-53F663BA24D4}";
    public static PermissionItem ClassificationDataAuditRead => new PermissionItem
    {
      Id = Guid.Parse(ClassificationDataAuditReadId),
      Category = MANAGE,
      Group = CLASSIFICATION_DATA_AUDIT,
      Action = PermissionAction.Read
    };

    //************************************************
    //DATA TABLE DATA AUDIT
    //************************************************
    // Dataset type Fact.
    public const string DataTableDataAuditReadId = "{CA4192FB-AEAD-4B13-8EE5-4E12168176B6}";
    public static PermissionItem DataTableDataAuditRead => new PermissionItem
    {
      Id = Guid.Parse(DataTableDataAuditReadId),
      Category = MANAGE,
      Group = DATA_TABLE_DATA_AUDIT,
      Action = PermissionAction.Read
    };

    //************************************************
    //LOOKUP DATA AUDIT
    //************************************************
    public const string LookupDataAuditReadId = "{F3802CFC-6FDF-43CE-A3A7-F85B677859FB}";
    public static PermissionItem LookupDataAuditRead => new PermissionItem
    {
      Id = Guid.Parse(LookupDataAuditReadId),
      Category = MANAGE,
      Group = LOOKUP_DATA_AUDIT,
      Action = PermissionAction.Read
    };
  }
}
