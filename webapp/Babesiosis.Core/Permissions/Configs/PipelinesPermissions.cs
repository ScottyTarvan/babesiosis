using System;

namespace Babesiosis.Core.Permissions.Configs
{
  /// <summary>
  /// Permissions for the Pipelines area — the pipeline definitions themselves
  /// and the run logs they produce.
  /// </summary>
  public static class PipelinesPermissions
  {
    const string PIPELINES = "pipelines";
    const string PIPELINE = "pipeline";
    const string LOG = "log";
    const string EXPECTATION = "expectation";

    //************************************************
    //PIPELINE
    //************************************************
    public const string PipelineReadId = "{4551E890-2E28-4903-B530-BA55FB675ED7}";
    public static PermissionItem PipelineRead => new PermissionItem
    {
      Id = Guid.Parse(PipelineReadId),
      Category = PIPELINES,
      Group = PIPELINE,
      Action = PermissionAction.Read
    };

    public const string PipelineAddId = "{8C42BE1B-84D3-4B82-B9A9-4AFB69963FC5}";
    public static PermissionItem PipelineAdd => new PermissionItem
    {
      Id = Guid.Parse(PipelineAddId),
      Category = PIPELINES,
      Group = PIPELINE,
      Action = PermissionAction.Add
    };

    public const string PipelineEditId = "{3B5AEE67-3B18-46E0-B227-3872A2819059}";
    public static PermissionItem PipelineEdit => new PermissionItem
    {
      Id = Guid.Parse(PipelineEditId),
      Category = PIPELINES,
      Group = PIPELINE,
      Action = PermissionAction.Edit
    };

    public const string PipelineDeleteId = "{506C5E52-1B0C-491F-8211-C919C1195F35}";
    public static PermissionItem PipelineDelete => new PermissionItem
    {
      Id = Guid.Parse(PipelineDeleteId),
      Category = PIPELINES,
      Group = PIPELINE,
      Action = PermissionAction.Delete
    };

    //************************************************
    //LOG
    //************************************************
    // Logs are written by the pipeline runner, never by a user, so Read is the
    // only action the UI gates.
    public const string LogReadId = "{ED089DA3-56A5-4EBC-990B-4B74F869D30D}";
    public static PermissionItem LogRead => new PermissionItem
    {
      Id = Guid.Parse(LogReadId),
      Category = PIPELINES,
      Group = LOG,
      Action = PermissionAction.Read
    };

    //************************************************
    //EXPECTATION
    //************************************************
    public const string ExpectationReadId = "{C86DD06B-327F-499C-8B04-E49E2C369E46}";
    public static PermissionItem ExpectationRead => new PermissionItem
    {
      Id = Guid.Parse(ExpectationReadId),
      Category = PIPELINES,
      Group = EXPECTATION,
      Action = PermissionAction.Read
    };

    public const string ExpectationAddId = "{ECC5C22D-C4ED-4A13-945D-571162F94193}";
    public static PermissionItem ExpectationAdd => new PermissionItem
    {
      Id = Guid.Parse(ExpectationAddId),
      Category = PIPELINES,
      Group = EXPECTATION,
      Action = PermissionAction.Add
    };

    public const string ExpectationEditId = "{1AC61B69-970C-4C6E-B1FB-DFC56E284BB5}";
    public static PermissionItem ExpectationEdit => new PermissionItem
    {
      Id = Guid.Parse(ExpectationEditId),
      Category = PIPELINES,
      Group = EXPECTATION,
      Action = PermissionAction.Edit
    };

    public const string ExpectationDeleteId = "{15862415-4798-4066-8E53-DEBD70A20166}";
    public static PermissionItem ExpectationDelete => new PermissionItem
    {
      Id = Guid.Parse(ExpectationDeleteId),
      Category = PIPELINES,
      Group = EXPECTATION,
      Action = PermissionAction.Delete
    };

    public const string ExpectationAcknowledgeId = "{603CAD31-A453-41EA-A278-93165F2CAE11}";
    public static PermissionItem ExpectationAcknowledge => new PermissionItem
    {
      Id = Guid.Parse(ExpectationAcknowledgeId),
      Category = PIPELINES,
      Group = EXPECTATION,
      Action = PermissionAction.Run
    };
  }
}
