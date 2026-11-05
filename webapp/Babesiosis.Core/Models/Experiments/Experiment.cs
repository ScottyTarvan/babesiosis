using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>One analysis run over a dataset (dbo.experiment), loaded from core/data/experiments/&lt;code&gt;.json.</summary>
  public class Experiment
  {
    public int Id { get; set; }
    /// <summary>Stable code, e.g. EXP01-DS05-pairwise.</summary>
    public string Code { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    /// <summary>pairwise_association, clustering, ...; the UI picks its visualisation by this.</summary>
    public string Method { get; set; }
    public int? DatasetId { get; set; }
    /// <summary>The run's settings, JSON, verbatim from the script.</summary>
    public string Parameters { get; set; }
    public string Script { get; set; }
    public string ScriptVersion { get; set; }
    public DateTime? RunAt { get; set; }
    public int? SubjectCount { get; set; }
    public int? VariableCount { get; set; }
    public int? TestCount { get; set; }
    /// <summary>Plain-text summary written by the script.</summary>
    public string Summary { get; set; }
    public DateTime LoadedAt { get; set; }

    public virtual Dataset Dataset { get; set; }
    public virtual ICollection<Association> Associations { get; set; } = new List<Association>();
    public virtual ICollection<ExperimentResult> Results { get; set; } = new List<ExperimentResult>();
    public virtual ICollection<ClusterAssignment> ClusterAssignments { get; set; } = new List<ClusterAssignment>();
  }
}
