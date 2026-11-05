namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>A subject's cluster in a clustering experiment (dbo.cluster_assignment).</summary>
  public class ClusterAssignment
  {
    public int ExperimentId { get; set; }
    public int SubjectId { get; set; }
    public string ClusterLabel { get; set; }
    /// <summary>Silhouette or membership strength.</summary>
    public double? Score { get; set; }

    public virtual Experiment Experiment { get; set; }
    public virtual Subject Subject { get; set; }
  }
}
