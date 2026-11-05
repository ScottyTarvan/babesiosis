namespace Babesiosis.Core.Api.Experiments.Commands
{
  /// <summary>
  /// Loads one experiment with its dataset, variable dictionary, associations and result
  /// payloads, for the Experiments screen's right-hand panel.
  /// </summary>
  public class GetExperimentDetailCommand
  {
    /// <summary>The experiment code, e.g. EXP01-DS05-pairwise.</summary>
    public string Code { get; set; }
    /// <summary>When true, only associations significant after adjustment are returned.</summary>
    public bool SignificantOnly { get; set; }
    /// <summary>When false, pairs where one variable is an arithmetic function of the other are left out.</summary>
    public bool IncludeTrivial { get; set; } = true;
    /// <summary>
    /// Cap on the association rows returned, best adjusted p first. Default 5000, enough
    /// for every pair of a 100-variable run; a proteome-scale run needs the filters.
    /// </summary>
    public int MaxAssociations { get; set; } = 5000;
  }
}
