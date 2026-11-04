using Babesiosis.Core.Configurations;
using Babesiosis.Core.Diagnostics;
using Babesiosis.Core.Exceptions;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Security;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System;
using System.Security;
using System.Text;

namespace Babesiosis.Core.Functions
{
  public class HttpFunctionBase : FunctionBase
  {
    private const string AUTHORIZATION = "Authorization";

    private readonly IAppSettings _appSettings;
    private readonly IJwtTokenGenerator _tokenProvider;
    private readonly ILogger _logger;

    public HttpFunctionBase(IAppSettingsService appSettingsService,
      IJwtTokenGenerator tokenProvider, 
      ILogger logger)
    {
      _appSettings = appSettingsService.GetAppSettings();
      _tokenProvider = tokenProvider;
      _logger = logger;
    }

    protected IAppSettings AppSettings => _appSettings;
    protected ILogger Logger => _logger;

    protected Task<IActionResult> ExecuteRequest(HttpRequest request, 
      Func<HttpRequest, Task<IActionResult>> body) 
    {
      return Execute(request, body, requireJwt: true, "An unhandled error occurred");
    }

    protected async Task<IActionResult> ExecuteRequest(HttpRequest request, 
      Func<HttpRequest, Task<IActionResult>> body, 
      string message = "An unhandled error occurred")
    {
      return await Execute(request, body, requireJwt: true, message);
    }

    protected async Task<IActionResult> ExecuteRequest(HttpRequest request,
      Func<HttpRequest, Task<IActionResult>> body,
      bool requireJwt,
      string message = "An unhandled error occurred")
    {
      return await Execute(request, body, requireJwt: requireJwt, message);
    }

    private async Task<IActionResult> Execute(HttpRequest request,  
      Func<HttpRequest, Task<IActionResult>> body,
      bool requireJwt,
      string message)
    {
      // Null unless DM_REQUEST_TIMINGS is set, and `using` on a null is a no-op —
      // so an un-instrumented host pays one environment-variable read per process
      // and nothing per request.
      using var timings = RequestTimings.BeginRequest(request?.Path.Value);

      try
      {
        if (requireJwt)
        {
          using (RequestTimings.Time("jwt.validate"))
          {
            ValidateJwtToken(request);
          }
        }
        SetHeaders(request);


        return await body.Invoke(request);
      }
      catch (SecurityException ex)
      {
        Logger.LogError(ex, ex.Unwrap().Message);
        return new UnauthorizedResult();
      }
      catch (ConcurrencyException ex)
      {
        Logger.LogError(ex, ex.Unwrap().Message);
        return new ConflictObjectResult(ex.Unwrap().Message.TruncateWithEllipsis(100));
      }
      catch (CodedValidationException ex)
      {
        // Must be caught before the plain ValidationException clause below: C# matches the
        // first assignable catch, and CodedValidationException derives from ValidationException,
        // so if that clause came first this one would never run. Same "rule the caller broke, not
        // a fault" reasoning as the plain-ValidationException branch below — logged as a warning
        // for the same reason — but the SPA also gets the machine-readable Code (and any Errors
        // detail, e.g. REQUIRED_FIELDS_UNBOUND's offending field names) and the exception's own
        // StatusCode instead of the fixed 400.
        Logger.LogWarning(ex, ex.Message);
        return new ObjectResult(new ErrorResponse { Message = ex.Message, Code = ex.Code, Errors = ex.Errors })
        {
          StatusCode = ex.StatusCode
        };
      }
      catch (ValidationException ex)
      {
        // A rule the caller broke, not a fault. Its message was written for them — "these datasets
        // are still attached", "a linked service with that name already exists" — so it is
        // returned as-is rather than replaced by this endpoint's generic string, which is what
        // the handler below would do and what left every assertion message invisible to the SPA.
        //
        // Logged as a warning, not an error: nothing is broken, and these would otherwise drown
        // out real faults.
        Logger.LogWarning(ex, ex.Message);
        return new BadRequestObjectResult(new ErrorResponse { Message = ex.Message });
      }
      catch (Exception ex)
      {
        Logger.LogError(ex, ex.Unwrap().Message);
        return new ServerErrorResult(new ErrorResponse
        {
          Message = message,
          Detail = ex.Message
        });
      }
      finally
      {
        // In the finally, not after the return: a failed request is often the
        // slow one, and its breakdown is the one worth having.
        FlushTimings(request, timings);
      }
    }

    /// <summary>
    /// Writes the request's timing breakdown to the console and the log, and
    /// echoes it on the response as <c>Server-Timing</c>.
    ///
    /// <para>
    /// The header runs BEFORE the IActionResult is executed — the result is only
    /// returned here, and the worker serializes it afterwards — so the headers
    /// have not been sent yet. <c>HasStarted</c> is still checked, because a
    /// streamed or already-flushed response would otherwise throw from a purely
    /// diagnostic code path.
    /// </para>
    ///
    /// <para>
    /// <b>Console.WriteLine, not just ILogger.</b> <c>Program.cs</c> calls
    /// <c>ConfigureFunctionsApplicationInsights()</c>, which installs a filter
    /// rule that drops worker logs below Warning — so an
    /// <c>ILogger.LogInformation</c> here reaches neither the <c>func</c> console
    /// nor anywhere else, which is exactly what happened the first time this ran.
    /// Writing to stdout sidesteps the logging pipeline entirely, and the worker's
    /// stdout is what the host prints. The log call is kept alongside it so the
    /// breakdown still reaches Application Insights on a deployed host, where
    /// there is no console to read.
    /// </para>
    /// </summary>
    private void FlushTimings(HttpRequest request, RequestTimingScope timings)
    {
      if (timings == null || !timings.HasEntries)
      {
        return;
      }

      var response = request?.HttpContext?.Response;

      if (response != null && !response.HasStarted)
      {
        try
        {
          response.Headers[RequestTimings.HeaderName] = timings.ToServerTiming();
        }
        catch (Exception ex)
        {
          // Never let instrumentation fail a request that otherwise succeeded.
          // The log line below still carries everything the header would have.
          Logger.LogWarning(ex, "Could not attach the {Header} header.", RequestTimings.HeaderName);
        }
      }

      var breakdown = timings.Format();

      // Bracketed by blank lines so it stays readable in a console that
      // Application Insights' developer-mode telemetry is flooding.
      Console.WriteLine();
      Console.WriteLine("[timings] " + breakdown);
      Console.WriteLine();

      Logger.LogInformation("[timings] {Breakdown}", breakdown);
    }

    private void SetHeaders(HttpRequest request)
    {
      if (request.HttpContext.Request.Headers.ContainsKey("fit-server-error-page"))
      {
        request.HttpContext.Response.Headers["fit-server-error-page"] = "true";
      }
    }
    
    protected void ValidateJwtToken(HttpRequest req)
    {
      if(!req.Headers.ContainsKey(AUTHORIZATION))
      {
        throw new SecurityException("Request does not contain a jwt token");
      }

      var token = req.Headers[AUTHORIZATION];

      var valid = _tokenProvider.ValidateToken(token);
      
      if(!valid)
      {
        throw new SecurityException("Security token has expired");
      }
    }

    protected Guid GetUserId(HttpRequest req)
    {
      var token = req.Headers[AUTHORIZATION];
      if (String.IsNullOrEmpty(token))
      {
        throw new NullReferenceException("Token cannot be null or empty");
      }
      return _tokenProvider.GetUserId(token);
    }
  }
}
