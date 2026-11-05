namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>One tested pair of variables in an experiment (dbo.association).</summary>
  public class Association
  {
    public int Id { get; set; }
    public int ExperimentId { get; set; }
    public int VariableAId { get; set; }
    public int VariableBId { get; set; }
    /// <summary>spearman, mann_whitney, kruskal_wallis or chi_square.</summary>
    public string Test { get; set; }
    /// <summary>rho, eta squared or Cramer's V; see <see cref="EstimateLabel"/>.</summary>
    public double? Estimate { get; set; }
    public string EstimateLabel { get; set; }
    /// <summary>Complete cases the test used.</summary>
    public int N { get; set; }
    /// <summary>Permutation p value.</summary>
    public double? PValue { get; set; }
    /// <summary>Benjamini-Hochberg adjusted across the run.</summary>
    public double? PAdjusted { get; set; }
    public bool Significant { get; set; }
    /// <summary>True when one variable is an arithmetic function of the other; never a finding.</summary>
    public bool Trivial { get; set; }
    /// <summary>"positive", "negative", or the group with the higher median.</summary>
    public string Direction { get; set; }
    /// <summary>JSON: statistic, group sizes and medians, or the contingency table.</summary>
    public string Detail { get; set; }

    public virtual Experiment Experiment { get; set; }
    public virtual Variable VariableA { get; set; }
    public virtual Variable VariableB { get; set; }
  }
}
