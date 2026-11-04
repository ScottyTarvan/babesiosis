namespace Babesiosis.Core.Services
{
  /// <summary>
  /// Per-invocation record of whether the caller was already authorized at the
  /// function layer by a <c>[RequiredPermission]</c> attribute.
  ///
  /// This is the bridge between the two permission models. Controllers are
  /// shared between the legacy application and the new one, and they assert
  /// legacy subject/action grants inline. When a request arrives through a
  /// function that carries a <c>[RequiredPermission]</c> attribute, the
  /// middleware has already made a stricter, code-declared decision — so the
  /// inline legacy assert would only be able to reject a caller the new model
  /// has already admitted.
  ///
  /// Endpoints without the attribute never set this flag, so the legacy
  /// application's requests are asserted exactly as they always were.
  /// </summary>
  public interface IPermissionContext
  {
    bool IsPreAuthorized { get; }

    void MarkPreAuthorized();
  }
}
