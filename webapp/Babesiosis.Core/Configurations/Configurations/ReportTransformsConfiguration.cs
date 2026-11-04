namespace Babesiosis.Core.Configurations.Configurations
{
  public class ReportTransformsConfiguration
  {
    /// <summary>
    /// Seconds a single transform command may run for. 30 is SqlCommand's own default, so an
    /// absent setting keeps the behaviour every existing transform was authored against.
    /// </summary>
    public int CommandTimeoutSeconds { get; set; }

    /// <summary>
    /// Seconds an authoring TEST run may take. Deliberately shorter than
    /// <see cref="CommandTimeoutSeconds"/>: someone is sitting in front of the dialog waiting,
    /// and the function host's own request window is what a longer wait would run into.
    /// </summary>
    public int TestCommandTimeoutSeconds { get; set; }

    /// <summary>
    /// Rows an authoring TEST run returns. The test proves the shape of the result set, not its
    /// size, so the rest is discarded rather than sent to a dialog that cannot show it.
    /// </summary>
    public int TestRowLimit { get; set; }
  }
}
