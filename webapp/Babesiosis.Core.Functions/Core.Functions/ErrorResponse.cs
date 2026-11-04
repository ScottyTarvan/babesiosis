using System.Text.Json.Serialization;

namespace Babesiosis.Core.Functions
{
  // Structured error body returned to the SPA. Detail carries the root-cause
  // message (non-production only); CorrelationId ties a user's report to the
  // full exception logged server-side.
  //
  // Code and Errors are additive, for CodedValidationException (see
  // source-to-dataset-mapping-brief.md §4): Code is a machine-readable string the SPA can
  // branch on, Errors is an optional structured detail payload (e.g. the offending field
  // names). Function responses go through ASP.NET Core's System.Text.Json formatter — see
  // Program.cs's ConfigureFunctionsWebApplication / Http.AspNetCore worker extension — so
  // WhenWritingNull is what keeps every existing response body's shape unchanged when a
  // plain ValidationException leaves them unset.
  public class ErrorResponse
  {
    public string Message { get; set; }
    public string Detail { get; set; }
    public string CorrelationId { get; set; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public string Code { get; set; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public object Errors { get; set; }
  }
}
