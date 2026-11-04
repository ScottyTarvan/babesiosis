namespace Babesiosis.Core.Configurations.Configurations
{
  public class QueuesConfiguration
  {
    public string Email { get; set; }
    public string Deployment { get; set; }
    /// <summary>Non-session queue of approve / decline / terminate signals for deployment runs (datasets-deployment.md §3.4.1).</summary>
    public string DeploymentTrigger { get; set; }
    public string Workflow { get; set; }
    public string Status { get; set; }
    public string ReportExecution { get; set; }
    public string ReportBatch { get; set; }
    public string EventTrigger { get; set; }
    public string PipelineLog { get; set; }
    public string PermissionsCacheRetry { get; set; }
    public string ExpectationResult { get; set; }
  }
}
