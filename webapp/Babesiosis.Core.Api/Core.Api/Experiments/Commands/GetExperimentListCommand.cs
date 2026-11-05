namespace Babesiosis.Core.Api.Experiments.Commands
{
  /// <summary>
  /// Loads the list of experiment runs for the Experiments screen's left-hand panel.
  /// Every run is returned; the panel filters client-side, since even a few hundred
  /// rows are light. Filters move server-side when the list outgrows that.
  /// </summary>
  public class GetExperimentListCommand
  {
    /// <summary>Optional: only runs over this dataset code, e.g. DS05.</summary>
    public string DatasetCode { get; set; }
  }
}
