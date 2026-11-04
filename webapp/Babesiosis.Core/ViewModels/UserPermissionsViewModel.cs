namespace Babesiosis.Core.ViewModels
{
  /// <summary>
  /// The coarse navigation flags that ship with the authenticated user — one per
  /// permission category, used by the shell to decide which modules to offer.
  ///
  /// These are a convenience for rendering the module switcher, not an
  /// authorisation boundary. Every screen behind them is gated server-side, and
  /// the per-screen detail arrives on each endpoint's own response rather than
  /// here. The flat subject/action grant list that used to ride along with this
  /// model was removed with the client-side ability checks it existed to feed.
  /// </summary>
  public class UserPermissionsViewModel
  {
    public bool CanViewManage { get; set; }
    public bool CanViewPipelines { get; set; }
    public bool CanViewReporting { get; set; }
    public bool CanViewSetup { get; set; }
    public bool CanViewTeams { get; set; }

    /// <summary>
    /// The Data sidebar's Health (<c>/health</c>) entry: the user holds Data Health
    /// Dashboard Read or Edit (Edit implies Read). Item-level, not category-level,
    /// because the items sit in the Setup category.
    /// </summary>
    public bool CanViewDataHealth { get; set; }

    /// <summary>
    /// The Setup › Statistics sidebar entry: the user holds Data Health Collector
    /// Settings Read or Edit (Edit implies Read).
    /// </summary>
    public bool CanViewStatistics { get; set; }
  }
}
