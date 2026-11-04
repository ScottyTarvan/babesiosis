using System;

namespace Babesiosis.Core.Exceptions
{
  /// <summary>
  /// The machine-readable codes an MCP tool error starts with (platform/mcp-server.md §3.5, §3.8).
  /// The tool error text the client sees is <see cref="McpToolException.Message"/>, which always
  /// starts with one of these.
  /// </summary>
  public static class McpToolErrorCodes
  {
    /// <summary>Steps 1 and 2 of §3.5: no, unknown, revoked or expired token, or no owner.</summary>
    public const string Unauthenticated = "unauthenticated";

    /// <summary>Steps 3 and 4 of §3.5: the message is <c>forbidden: &lt;permission name&gt;</c>.</summary>
    public const string Forbidden = "forbidden";

    /// <summary>A dataset id or name that resolves to nothing (§3.8).</summary>
    public const string NotFound = "not-found";

    /// <summary>A dataset name that matches more than one dataset (§3.8, PL-75).</summary>
    public const string Ambiguous = "ambiguous";

    /// <summary>Tool arguments that cannot be acted on (no dataset id or name, for example).</summary>
    public const string Invalid = "invalid";

    /// <summary>
    /// A named failure with a fixed text, such as <c>error: the activator could not be published.</c>
    /// (§3.5, §3.28). Never carries exception text.
    /// </summary>
    public const string Error = "error";
  }

  /// <summary>
  /// A refused MCP tool call. Never carries data: the function returns <see cref="Exception.Message"/>
  /// as the tool error and nothing else (platform/mcp-server.md §3.5 "never any data").
  ///
  /// <para>
  /// Deliberately NOT a <see cref="ValidationException"/> / <see cref="InvalidOperationException"/>:
  /// an HTTP-style handler that maps those to 400 must not be able to swallow an authentication
  /// failure and answer it as a validation message.
  /// </para>
  ///
  /// <para>
  /// <see cref="UserId"/> and <see cref="TokenPrefix"/> are set once the caller is known (a
  /// <c>forbidden</c> or later failure) so the function can log the outcome with the user and the
  /// token prefix (§3.12). An <c>unauthenticated</c> failure carries the prefix only, and only when
  /// the token was found. Neither is the secret; the secret and the Authorization header never
  /// reach this type.
  /// </para>
  /// </summary>
  public class McpToolException : Exception
  {
    public string Code { get; }

    public Guid? UserId { get; }

    public string TokenPrefix { get; }

    public McpToolException(string code, string message, Guid? userId = null, string tokenPrefix = null)
      : base(message)
    {
      Code = code;
      UserId = userId;
      TokenPrefix = tokenPrefix;
    }

    /// <summary>
    /// <paramref name="tokenPrefix"/> is set when the token was found but is not active (revoked,
    /// expired, deleted owner), for the log line only; the user is never set (§3.12). The message is
    /// always just <c>unauthenticated</c>.
    /// </summary>
    public static McpToolException Unauthenticated(string tokenPrefix = null)
    {
      return new McpToolException(McpToolErrorCodes.Unauthenticated, McpToolErrorCodes.Unauthenticated,
        null, tokenPrefix);
    }

    public static McpToolException Forbidden(string permissionName, Guid userId, string tokenPrefix)
    {
      return new McpToolException(McpToolErrorCodes.Forbidden,
        $"{McpToolErrorCodes.Forbidden}: {permissionName}", userId, tokenPrefix);
    }

    public static McpToolException NotFound(string detail, Guid userId, string tokenPrefix)
    {
      return new McpToolException(McpToolErrorCodes.NotFound,
        $"{McpToolErrorCodes.NotFound}: {detail}", userId, tokenPrefix);
    }

    public static McpToolException Ambiguous(string detail, Guid userId, string tokenPrefix)
    {
      return new McpToolException(McpToolErrorCodes.Ambiguous,
        $"{McpToolErrorCodes.Ambiguous}: {detail}", userId, tokenPrefix);
    }

    public static McpToolException Invalid(string detail, Guid userId, string tokenPrefix)
    {
      return new McpToolException(McpToolErrorCodes.Invalid,
        $"{McpToolErrorCodes.Invalid}: {detail}", userId, tokenPrefix);
    }

    /// <summary>
    /// The publish of a real <c>run_activator</c> call failed (platform/mcp-server.md §3.5, §3.28).
    /// The text is fixed: the failure detail is in the Failed run record's message, never here.
    /// </summary>
    public static McpToolException ActivatorPublishFailed(Guid userId, string tokenPrefix)
    {
      return new McpToolException(McpToolErrorCodes.Error,
        $"{McpToolErrorCodes.Error}: the activator could not be published.", userId, tokenPrefix);
    }
  }
}
