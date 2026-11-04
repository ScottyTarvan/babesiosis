using Babesiosis.Core.Permissions.Attributes;
using Babesiosis.Core.Security;
using Babesiosis.Core.Services;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Azure.Functions.Worker.Middleware;
using Microsoft.Extensions.DependencyInjection;
using System.Collections.Concurrent;
using System.Reflection;

namespace Babesiosis.Core.Functions.Middleware
{
  /// <summary>
  /// Enforces <see cref="RequiredPermissionAttribute"/> on function entry
  /// points before the function body runs.
  ///
  /// Present in every isolated-worker function app that enforces the
  /// code-declared permission model — Core.Functions and Reports.Functions
  /// today, one copy per app (keep them identical). It lives here rather than in
  /// Babesiosis.Core so that the non-Functions consumers of Core do
  /// not acquire the worker packages.
  ///
  /// A function with no attribute passes straight through untouched. That is
  /// what keeps every pre-existing endpoint — all of which the legacy
  /// application still calls — behaving exactly as it did before: they carry no
  /// attribute, so they continue to rely on the subject/action
  /// <c>IUserPermissionsService.Assert</c> checks inside their controllers.
  /// </summary>
  public class RequiredPermissionsMiddleware : IFunctionsWorkerMiddleware
  {
    private const string AUTHORIZATION = "Authorization";
    private const string BEARER_PREFIX = "Bearer ";

    /// <summary>
    /// Entry point -> attribute. Reflection over the function assembly is far
    /// too expensive to repeat per invocation, and the mapping never changes
    /// for the lifetime of the worker. A null value is cached too, so
    /// unattributed functions cost one dictionary lookup.
    /// </summary>
    private static readonly ConcurrentDictionary<string, RequiredPermissionAttribute> _attributes = new();

    public async Task Invoke(FunctionContext context, FunctionExecutionDelegate next)
    {
      var attribute = GetAttribute(context);
      if (attribute == null)
      {
        await next(context);
        return;
      }

      var httpContext = context.GetHttpContext();
      if (httpContext == null)
      {
        // A permission attribute on a non-HTTP trigger has no caller to check.
        // Treat it as a wiring mistake rather than silently allowing it.
        Deny(context, StatusCodes.Status403Forbidden,
          $"[RequiredPermission] is only supported on HTTP triggers ({context.FunctionDefinition.Name}).");
        return;
      }

      var token = ReadToken(httpContext);
      if (string.IsNullOrWhiteSpace(token))
      {
        Deny(context, StatusCodes.Status401Unauthorized, "Authentication required.");
        return;
      }

      var tokenGenerator = context.InstanceServices.GetRequiredService<IJwtTokenGenerator>();

      Guid userId;
      try
      {
        if (!tokenGenerator.ValidateToken(token))
        {
          Deny(context, StatusCodes.Status401Unauthorized, "Security token has expired.");
          return;
        }

        userId = tokenGenerator.GetUserId(token);
      }
      catch
      {
        Deny(context, StatusCodes.Status401Unauthorized, "Authentication required.");
        return;
      }

      var permissionsService = context.InstanceServices.GetRequiredService<IUserPermissionItemsService>();
      var permissions = await permissionsService.GetUserPermissionsAsync(userId);

      // Multiple ids on one attribute are OR-ed — any single grant admits.
      var permitted = attribute.PermissionIds
        .Any(id => Guid.TryParse(id, out var parsed) && permissions.HasPermission(parsed));

      if (!permitted)
      {
        Deny(context, StatusCodes.Status403Forbidden, $"You are not allowed to {attribute}");
        return;
      }

      // Tell the shared controllers this request has already been authorized
      // against the code-declared model, so their inline legacy subject/action
      // asserts stand down. See IPermissionContext.
      context.InstanceServices.GetRequiredService<IPermissionContext>().MarkPreAuthorized();

      await next(context);
    }

    private static string ReadToken(HttpContext httpContext)
    {
      if (!httpContext.Request.Headers.TryGetValue(AUTHORIZATION, out var values))
      {
        return null;
      }

      var raw = values.FirstOrDefault();
      if (string.IsNullOrWhiteSpace(raw))
      {
        return null;
      }

      // The web client sends the bare token; other callers may send it with the
      // Bearer prefix. Accept both.
      return raw.StartsWith(BEARER_PREFIX, StringComparison.OrdinalIgnoreCase)
        ? raw[BEARER_PREFIX.Length..].Trim()
        : raw.Trim();
    }

    private static void Deny(FunctionContext context, int statusCode, string message)
    {
      var result = context.GetInvocationResult();
      result.Value = new ObjectResult(new { message })
      {
        StatusCode = statusCode
      };
    }

    private static RequiredPermissionAttribute GetAttribute(FunctionContext context)
    {
      var entryPoint = context.FunctionDefinition.EntryPoint;

      return _attributes.GetOrAdd(entryPoint, _ =>
      {
        var separator = entryPoint.LastIndexOf('.');
        if (separator <= 0)
        {
          return null;
        }

        var typeName = entryPoint[..separator];
        var methodName = entryPoint[(separator + 1)..];

        var assembly = Assembly.LoadFrom(context.FunctionDefinition.PathToAssembly);
        var type = assembly.GetType(typeName);

        return type?.GetMethod(methodName)?.GetCustomAttribute<RequiredPermissionAttribute>();
      });
    }
  }
}
