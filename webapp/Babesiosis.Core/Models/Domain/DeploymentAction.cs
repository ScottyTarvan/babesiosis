using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum DeploymentAction : byte
  {
    None = 0,
    [Description("Deploy")]
    Deploy = 1,
    [Description("Delete")]
    Delete = 2,
    [Description("Patch")]
    Patch = 3,
    [Description("Unlink")]
    Unlink = 4,
    [Description("Link")]
    Link = 5,
    /// <summary>
    /// One row action from the Diagnostics screen, executed as a run of its own: a single
    /// deployment step, no approval gate and no snapshot. It appears in the deployment log beside
    /// real deployments because that is where an operator looks for "what happened to my column",
    /// and because the run row and its step logs ARE the audit record for a write that reached the
    /// customer's database without a plan preview.
    /// </summary>
    [Description("Remediate")]
    Remediate = 6
  }
}
