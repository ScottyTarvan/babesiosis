namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>
  /// One method-specific output of an experiment as JSON (dbo.experiment_result): the Spearman matrix,
  /// the variable clusters, the top associations, the interpretation note, the run notes.
  /// </summary>
  public class ExperimentResult
  {
    public int Id { get; set; }
    public int ExperimentId { get; set; }
    /// <summary>spearman_matrix, variable_clusters, top_associations, interpretation, run_notes, ...</summary>
    public string Kind { get; set; }
    public string Title { get; set; }
    /// <summary>JSON payload whose shape depends on <see cref="Kind"/>.</summary>
    public string Payload { get; set; }
    public short SortOrder { get; set; }

    public virtual Experiment Experiment { get; set; }
  }
}
