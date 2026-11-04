namespace Babesiosis.Core.Services.Impl
{
  /// <summary>
  /// Registered scoped, so one instance exists per function invocation. The
  /// flag is write-once and only ever set by RequiredPermissionsMiddleware.
  /// </summary>
  public class PermissionContext : IPermissionContext
  {
    public bool IsPreAuthorized { get; private set; }

    public void MarkPreAuthorized()
    {
      IsPreAuthorized = true;
    }
  }
}
