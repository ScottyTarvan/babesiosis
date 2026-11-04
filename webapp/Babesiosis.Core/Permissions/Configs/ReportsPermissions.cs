using System;

namespace Babesiosis.Core.Permissions.Configs
{
  /// <summary>
  /// Permissions for the Reports area — the Setup screens that define a report
  /// (the report record, its schedules, its entities and its components), the
  /// Content hub that overrides what a report renders, the Run screens that
  /// execute reports and serve their instances, and the read-only Analyse
  /// screens.
  ///
  /// These are enforced by <c>Babesiosis.Reports.Functions</c>, a separate
  /// function app from Core. They are registered in both apps' Program.cs:
  /// Reports.Functions needs them to enforce <c>[RequiredPermission]</c>, and
  /// Core.Functions needs them so the role-permissions screen can offer them
  /// for granting.
  ///
  /// The legacy <c>reporting-*</c> subject/action <c>Assert</c> calls inside the
  /// report controllers stay in place until V1 dies; a request that clears the
  /// middleware is flagged pre-authorized and those asserts stand down. See
  /// IPermissionContext.
  ///
  /// Groups deliberately do not repeat the category: the setup report record is
  /// <c>report</c>, not <c>reports-report</c>.
  /// </summary>
  public static class ReportsPermissions
  {
    const string REPORTS = "reports";
    const string REPORT = "report";
    const string SCHEDULE = "schedule";
    const string RUN_SCHEDULE = "run-schedule";
    const string COMPONENT = "component";
    const string CONTENT = "content";
    const string CONTENT_COLOUR = "content-colour";
    const string CONTENT_COMMENTARY = "content-commentary";
    const string CONTENT_IMAGE = "content-image";
    const string CONTENT_PDF = "content-pdf";
    const string RUN_REPORT = "run-report";
    const string INSTANCE = "instance";
    const string INSTANCE_PREVIEW = "instance-preview";
    const string ANALYSE = "analyse";
    const string ANALYSE_DATA = "analyse-data";
    const string DISTRIBUTION = "distribution";
    const string CHANNEL = "channel";
    const string REPORT_DISTRIBUTION = "report-distribution";

    //************************************************
    //REPORT
    //************************************************
    // The report definition itself — the Setup list and its create/edit wizard.
    // Read also opens the report hub, from which the schedules, entities and
    // components tabs hang; each of those is separately gated by its own group's
    // Read, which is what the reports-setup-get canView* keys resolve from.
    public const string ReportReadId = "{8EC76547-9C94-4CA9-826E-3E9251ECD711}";
    public static PermissionItem ReportRead => new PermissionItem
    {
      Id = Guid.Parse(ReportReadId),
      Category = REPORTS,
      Group = REPORT,
      Action = PermissionAction.Read
    };

    public const string ReportAddId = "{713B5049-510C-401F-A3AD-482FDA24598F}";
    public static PermissionItem ReportAdd => new PermissionItem
    {
      Id = Guid.Parse(ReportAddId),
      Category = REPORTS,
      Group = REPORT,
      Action = PermissionAction.Add
    };

    public const string ReportEditId = "{762F09C5-0E96-4AD7-8804-53643A334154}";
    public static PermissionItem ReportEdit => new PermissionItem
    {
      Id = Guid.Parse(ReportEditId),
      Category = REPORTS,
      Group = REPORT,
      Action = PermissionAction.Edit
    };

    public const string ReportDeleteId = "{6F09ABA0-ABCA-4F5D-B783-4F9CE7514C5D}";
    public static PermissionItem ReportDelete => new PermissionItem
    {
      Id = Guid.Parse(ReportDeleteId),
      Category = REPORTS,
      Group = REPORT,
      Action = PermissionAction.Delete
    };

    //************************************************
    //SCHEDULE
    //************************************************
    // Archive and restore are Delete, not an action of their own. Archiving a
    // schedule is the only removal path the UI offers — there is no hard delete
    // — so the legacy delete grant and the Archive button are the same
    // authority, and restore is the undo of a delete the same holder performed.
    public const string ScheduleReadId = "{15EDF9BE-91A3-426B-80D4-9129DD012115}";
    public static PermissionItem ScheduleRead => new PermissionItem
    {
      Id = Guid.Parse(ScheduleReadId),
      Category = REPORTS,
      Group = SCHEDULE,
      Action = PermissionAction.Read
    };

    public const string ScheduleAddId = "{E3821E30-6BAE-43F6-85C3-33B1EAA06F6B}";
    public static PermissionItem ScheduleAdd => new PermissionItem
    {
      Id = Guid.Parse(ScheduleAddId),
      Category = REPORTS,
      Group = SCHEDULE,
      Action = PermissionAction.Add
    };

    public const string ScheduleEditId = "{1F8CDFBF-B55B-451B-82E3-5689E873E8D8}";
    public static PermissionItem ScheduleEdit => new PermissionItem
    {
      Id = Guid.Parse(ScheduleEditId),
      Category = REPORTS,
      Group = SCHEDULE,
      Action = PermissionAction.Edit
    };

    public const string ScheduleDeleteId = "{0577C47D-BBEF-49A6-AA31-A7653CF447C6}";
    public static PermissionItem ScheduleDelete => new PermissionItem
    {
      Id = Guid.Parse(ScheduleDeleteId),
      Category = REPORTS,
      Group = SCHEDULE,
      Action = PermissionAction.Delete
    };

    //************************************************
    //RUN SCHEDULE
    //************************************************
    // A schedule's runs, distinct from Setup's schedule group above. Run Now
    // deliberately reuses RunReportRun because it is a run, not a schedule
    // write; the timer sweep that fires scheduled runs asserts nothing, it is
    // not a user-initiated request.
    public const string RunScheduleReadId = "{87B4958D-A02D-4FB5-A219-AB7AB856F3C6}";
    public static PermissionItem RunScheduleRead => new PermissionItem
    {
      Id = Guid.Parse(RunScheduleReadId),
      Category = REPORTS,
      Group = RUN_SCHEDULE,
      Action = PermissionAction.Read
    };

    public const string RunScheduleAddId = "{588B896F-80D2-4CD5-B9BF-D06BD3EDBDCA}";
    public static PermissionItem RunScheduleAdd => new PermissionItem
    {
      Id = Guid.Parse(RunScheduleAddId),
      Category = REPORTS,
      Group = RUN_SCHEDULE,
      Action = PermissionAction.Add
    };

    public const string RunScheduleEditId = "{8C6CC7F3-616B-4234-8BF6-753C0B18722F}";
    public static PermissionItem RunScheduleEdit => new PermissionItem
    {
      Id = Guid.Parse(RunScheduleEditId),
      Category = REPORTS,
      Group = RUN_SCHEDULE,
      Action = PermissionAction.Edit
    };

    public const string RunScheduleDeleteId = "{B18D2004-667A-4223-83BF-4F4F6ED92155}";
    public static PermissionItem RunScheduleDelete => new PermissionItem
    {
      Id = Guid.Parse(RunScheduleDeleteId),
      Category = REPORTS,
      Group = RUN_SCHEDULE,
      Action = PermissionAction.Delete
    };

    //************************************************
    //COMPONENT
    //************************************************
    // Reordering components, and reordering the elements inside one, is Edit —
    // the order is a property of the component, not a record of its own. Same
    // call SetupPermissions makes for dataset index fields and event trigger
    // parameters.
    public const string ComponentReadId = "{8F4433A0-55EB-4A46-83AB-F396B3E8EE24}";
    public static PermissionItem ComponentRead => new PermissionItem
    {
      Id = Guid.Parse(ComponentReadId),
      Category = REPORTS,
      Group = COMPONENT,
      Action = PermissionAction.Read
    };

    public const string ComponentAddId = "{C0523D70-64BC-4457-A94A-EAB28956059F}";
    public static PermissionItem ComponentAdd => new PermissionItem
    {
      Id = Guid.Parse(ComponentAddId),
      Category = REPORTS,
      Group = COMPONENT,
      Action = PermissionAction.Add
    };

    public const string ComponentEditId = "{792E1CAD-698A-4CD4-9893-BCEFC887D9ED}";
    public static PermissionItem ComponentEdit => new PermissionItem
    {
      Id = Guid.Parse(ComponentEditId),
      Category = REPORTS,
      Group = COMPONENT,
      Action = PermissionAction.Edit
    };

    public const string ComponentDeleteId = "{5584C440-79A0-4E48-9F73-80B199E3D37B}";
    public static PermissionItem ComponentDelete => new PermissionItem
    {
      Id = Guid.Parse(ComponentDeleteId),
      Category = REPORTS,
      Group = COMPONENT,
      Action = PermissionAction.Delete
    };

    //************************************************
    //CONTENT
    //************************************************
    // Opening the content landing screen and the content hub. The per-type
    // groups below carry the write authority; this one is the read gate for all
    // of them, so a hub panel is only reachable by a caller who already holds it.
    public const string ContentReadId = "{13E755DA-6784-4A3E-9BAF-51CD2B4AFAE7}";
    public static PermissionItem ContentRead => new PermissionItem
    {
      Id = Guid.Parse(ContentReadId),
      Category = REPORTS,
      Group = CONTENT,
      Action = PermissionAction.Read
    };

    //************************************************
    //CONTENT COLOUR
    //************************************************
    // The four content override types are separate groups because the legacy
    // grant is per type — one collapsed "content override" group would widen an
    // existing commentary-only grant to the colour, image and PDF panels too.
    public const string ContentColourEditId = "{86C92A63-ED5C-4D27-821D-73E75FC7E201}";
    public static PermissionItem ContentColourEdit => new PermissionItem
    {
      Id = Guid.Parse(ContentColourEditId),
      Category = REPORTS,
      Group = CONTENT_COLOUR,
      Action = PermissionAction.Edit
    };

    //************************************************
    //CONTENT COMMENTARY
    //************************************************
    public const string ContentCommentaryEditId = "{614BD839-DDA6-4B54-A168-200DB381AB26}";
    public static PermissionItem ContentCommentaryEdit => new PermissionItem
    {
      Id = Guid.Parse(ContentCommentaryEditId),
      Category = REPORTS,
      Group = CONTENT_COMMENTARY,
      Action = PermissionAction.Edit
    };

    //************************************************
    //CONTENT IMAGE
    //************************************************
    public const string ContentImageEditId = "{D640F7D7-0740-49D2-8816-9263C9788594}";
    public static PermissionItem ContentImageEdit => new PermissionItem
    {
      Id = Guid.Parse(ContentImageEditId),
      Category = REPORTS,
      Group = CONTENT_IMAGE,
      Action = PermissionAction.Edit
    };

    //************************************************
    //CONTENT PDF
    //************************************************
    // The only content type with a Download: a stored PDF override can be pulled
    // back out of the hub, which the colour, commentary and image panels have no
    // equivalent of.
    public const string ContentPdfEditId = "{82992337-7B56-4F43-8C0B-789A02220875}";
    public static PermissionItem ContentPdfEdit => new PermissionItem
    {
      Id = Guid.Parse(ContentPdfEditId),
      Category = REPORTS,
      Group = CONTENT_PDF,
      Action = PermissionAction.Edit
    };

    public const string ContentPdfDownloadId = "{9F92FDD9-A779-434D-969E-C2EB01152C11}";
    public static PermissionItem ContentPdfDownload => new PermissionItem
    {
      Id = Guid.Parse(ContentPdfDownloadId),
      Category = REPORTS,
      Group = CONTENT_PDF,
      Action = PermissionAction.Download
    };

    //************************************************
    //RUN REPORT
    //************************************************
    // Distinct from the report group: holding Setup's report:read does not admit
    // the Run screens, and a user who may run a report generally may not redefine
    // it. Run covers both run and rerun — a rerun is a run of the same report.
    public const string RunReportReadId = "{33817664-6D50-47C3-A356-31D574AA0D4F}";
    public static PermissionItem RunReportRead => new PermissionItem
    {
      Id = Guid.Parse(RunReportReadId),
      Category = REPORTS,
      Group = RUN_REPORT,
      Action = PermissionAction.Read
    };

    public const string RunReportRunId = "{3C293A45-9380-4ED0-BA05-06AEB1BF0261}";
    public static PermissionItem RunReportRun => new PermissionItem
    {
      Id = Guid.Parse(RunReportRunId),
      Category = REPORTS,
      Group = RUN_REPORT,
      Action = PermissionAction.Run
    };

    public const string RunReportDownloadId = "{1A5D420A-5AE7-47A7-9C53-C00197786837}";
    public static PermissionItem RunReportDownload => new PermissionItem
    {
      Id = Guid.Parse(RunReportDownloadId),
      Category = REPORTS,
      Group = RUN_REPORT,
      Action = PermissionAction.Download
    };

    //************************************************
    //INSTANCE
    //************************************************
    // A rendered run of a report, and its versions. Read is the instance list
    // and its version history — the metadata rows, not the artifact. Download
    // stays separate because it hands the caller a file they then retain, and
    // preview is its own group below.
    public const string InstanceReadId = "{20F707BB-EAEB-478E-A40A-D0E7324F6AFF}";
    public static PermissionItem InstanceRead => new PermissionItem
    {
      Id = Guid.Parse(InstanceReadId),
      Category = REPORTS,
      Group = INSTANCE,
      Action = PermissionAction.Read
    };

    public const string InstanceDownloadId = "{0E920693-3BB8-4AE2-B757-4376D1B35A20}";
    public static PermissionItem InstanceDownload => new PermissionItem
    {
      Id = Guid.Parse(InstanceDownloadId),
      Category = REPORTS,
      Group = INSTANCE,
      Action = PermissionAction.Download
    };

    //************************************************
    //INSTANCE PREVIEW
    //************************************************
    // Rendering an instance on screen, as opposed to listing the instances that
    // exist. Split out of the instance group rather than declared as a Preview
    // action so that seeing the list and seeing the report's contents are
    // independently grantable: a user who may audit that a run happened is not
    // thereby admitted to what it says. It is a group split for the same reason
    // analyse-data is split from analyse — the authority differs by resource,
    // not by verb, and preview is still a Read, of the artifact rather than of
    // the row that describes it.
    public const string InstancePreviewReadId = "{F0A0D322-7CF5-41C8-9677-13A207E753CE}";
    public static PermissionItem InstancePreviewRead => new PermissionItem
    {
      Id = Guid.Parse(InstancePreviewReadId),
      Category = REPORTS,
      Group = INSTANCE_PREVIEW,
      Action = PermissionAction.Read
    };

    //************************************************
    //ANALYSE
    //************************************************
    // Nav-level visibility of the Analyse area. The data behind it is gated
    // separately below, mirroring how ManagePermissions splits <type> from
    // <type>-data.
    public const string AnalyseReadId = "{88679420-C2A5-495B-8F70-97057D47AEBB}";
    public static PermissionItem AnalyseRead => new PermissionItem
    {
      Id = Guid.Parse(AnalyseReadId),
      Category = REPORTS,
      Group = ANALYSE,
      Action = PermissionAction.Read
    };

    //************************************************
    //ANALYSE DATA
    //************************************************
    // The analysis grid itself. Read-only: there is no write path anywhere in
    // Analyse, so Read and the export Download are the only actions.
    public const string AnalyseDataReadId = "{AE162C5A-F3BA-445E-97C8-B3DC778C42BD}";
    public static PermissionItem AnalyseDataRead => new PermissionItem
    {
      Id = Guid.Parse(AnalyseDataReadId),
      Category = REPORTS,
      Group = ANALYSE_DATA,
      Action = PermissionAction.Read
    };

    public const string AnalyseDataDownloadId = "{FFBCA09E-DAF3-4C50-B1E5-37386321C5E6}";
    public static PermissionItem AnalyseDataDownload => new PermissionItem
    {
      Id = Guid.Parse(AnalyseDataDownloadId),
      Category = REPORTS,
      Group = ANALYSE_DATA,
      Action = PermissionAction.Download
    };

    //************************************************
    //DISTRIBUTION
    //************************************************
    // Read admits both distribution screens (the deck and the drill-down
    // grid); approve and distribute are split because sign-off and release
    // are different authorities in a finance shop — the person who approves
    // a document is not necessarily who is trusted to release it outside
    // the system. Preview on the distribution grid reuses
    // InstancePreviewRead rather than declaring its own.
    public const string DistributionReadId = "{20A2F95D-06AF-409D-9E36-867FA6281FA7}";
    public static PermissionItem DistributionRead => new PermissionItem
    {
      Id = Guid.Parse(DistributionReadId),
      Category = REPORTS,
      Group = DISTRIBUTION,
      Action = PermissionAction.Read
    };

    public const string DistributionApproveId = "{82741961-0BF4-4969-84FA-9BFBD28F299C}";
    public static PermissionItem DistributionApprove => new PermissionItem
    {
      Id = Guid.Parse(DistributionApproveId),
      Category = REPORTS,
      Group = DISTRIBUTION,
      Action = PermissionAction.Approve
    };

    public const string DistributionDistributeId = "{0897A639-EAA5-4D60-AA14-9C1523D44655}";
    public static PermissionItem DistributionDistribute => new PermissionItem
    {
      Id = Guid.Parse(DistributionDistributeId),
      Category = REPORTS,
      Group = DISTRIBUTION,
      Action = PermissionAction.Distribute
    };
    //************************************************
    //CHANNEL
    //************************************************
    // The distribution channel catalogue (Setup ▸ Distribution Channels): the
    // per-environment list of Email / FTP / SFTP / WhatsApp destinations and
    // their vault-held configuration. Testing a connection is Read, exactly as
    // it is for linked services — it proves what is stored, it authors nothing.
    // Reading a channel's configuration document back is Edit, not Read: the
    // list never carries it, and the only screen that asks for it is the edit
    // dialog.
    public const string ChannelReadId = "{4C1E2B7A-9D3F-4E8B-A6C2-7F0D5B9E1A34}";
    public static PermissionItem ChannelRead => new PermissionItem
    {
      Id = Guid.Parse(ChannelReadId),
      Category = REPORTS,
      Group = CHANNEL,
      Action = PermissionAction.Read
    };

    public const string ChannelAddId = "{A8F3D6C1-2E4B-4F7A-9B5D-3C8E1F6A2D47}";
    public static PermissionItem ChannelAdd => new PermissionItem
    {
      Id = Guid.Parse(ChannelAddId),
      Category = REPORTS,
      Group = CHANNEL,
      Action = PermissionAction.Add
    };

    public const string ChannelEditId = "{5D9B2E7F-6A1C-4B3D-8E2F-9C4A7D1B6E58}";
    public static PermissionItem ChannelEdit => new PermissionItem
    {
      Id = Guid.Parse(ChannelEditId),
      Category = REPORTS,
      Group = CHANNEL,
      Action = PermissionAction.Edit
    };

    public const string ChannelDeleteId = "{E2C7A4D9-1B6F-4E8A-B3D5-6F9C2A8E4B71}";
    public static PermissionItem ChannelDelete => new PermissionItem
    {
      Id = Guid.Parse(ChannelDeleteId),
      Category = REPORTS,
      Group = CHANNEL,
      Action = PermissionAction.Delete
    };

    //************************************************
    //REPORT DISTRIBUTION
    //************************************************
    // Which channels a report goes out through, and the per-report settings on
    // each assignment. Read + Edit only, the entity group's shape: assigning a
    // channel toggles something that already exists in the catalogue, it does
    // not create a record with a lifecycle of its own. Read also gates the
    // Distribution row action on the reports list (canViewDistribution).
    public const string ReportDistributionReadId = "{7B4E9F2C-3D8A-4C1B-A5E7-2F6D9B3C8A15}";
    public static PermissionItem ReportDistributionRead => new PermissionItem
    {
      Id = Guid.Parse(ReportDistributionReadId),
      Category = REPORTS,
      Group = REPORT_DISTRIBUTION,
      Action = PermissionAction.Read
    };

    public const string ReportDistributionEditId = "{9F1C6D3E-8B2A-4D7F-B4C9-5E3A8F2D7C62}";
    public static PermissionItem ReportDistributionEdit => new PermissionItem
    {
      Id = Guid.Parse(ReportDistributionEditId),
      Category = REPORTS,
      Group = REPORT_DISTRIBUTION,
      Action = PermissionAction.Edit
    };
  }
}
