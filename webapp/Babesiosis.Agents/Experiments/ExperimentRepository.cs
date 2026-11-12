using System.Data;
using System.Text.Json;
using Babesiosis.Core.Configurations;
using Microsoft.Data.SqlClient;

namespace Babesiosis.Agents.Experiments
{
  /// <summary>
  /// Read-only access to the experiments for the agent's tools: <c>dbo.experiment</c> (one row
  /// per analysis run) and <c>dbo.experiment_result</c> (its outputs as JSON, one of them the
  /// <c>interpretation</c> text). The rows are written by the experiment packages; their content
  /// is defined in <c>/experiments/run-instructions.md</c>. These are the rows that the web app's
  /// Experiments screen shows.
  /// </summary>
  public sealed class ExperimentRepository
  {
    /// <summary>The result kind whose payload is the explanation: <c>{"sections":[{"heading","paragraphs"}]}</c>.</summary>
    public const string InterpretationKind = "interpretation";

    private readonly IAppSettingsService _appSettingsService;

    public ExperimentRepository(IAppSettingsService appSettingsService)
    {
      _appSettingsService = appSettingsService;
    }

    /// <summary>Every experiment, by code.</summary>
    public async Task<IReadOnlyList<ExperimentHeader>> ListAsync(CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT e.experiment_code, e.name, e.method, e.description, CAST(e.parameters AS NVARCHAR(MAX)) AS parameters,
               e.run_at, e.n_subjects, e.n_variables, e.n_tests, e.summary
        FROM dbo.experiment AS e
        ORDER BY e.experiment_code;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);

      var experiments = new List<ExperimentHeader>();
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
        experiments.Add(ReadHeader(reader));

      return experiments;
    }

    /// <summary>
    /// One experiment: its header, the list of its results (kind, title, size) and its
    /// interpretation payload. Null when the code does not exist.
    /// </summary>
    public async Task<ExperimentRecord?> GetAsync(string code, CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT e.experiment_code, e.name, e.method, e.description, CAST(e.parameters AS NVARCHAR(MAX)) AS parameters,
               e.run_at, e.n_subjects, e.n_variables, e.n_tests, e.summary
        FROM dbo.experiment AS e
        WHERE e.experiment_code = @code;

        SELECT r.result_kind, r.title, r.sort_order,
               LEN(CAST(r.payload AS NVARCHAR(MAX))) AS payload_chars,
               CASE WHEN r.result_kind = @interpretation THEN CAST(r.payload AS NVARCHAR(MAX)) END AS payload
        FROM dbo.experiment_result AS r
        JOIN dbo.experiment AS e ON e.experiment_id = r.experiment_id
        WHERE e.experiment_code = @code
        ORDER BY r.sort_order, r.result_id;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      command.Parameters.Add("@code", SqlDbType.VarChar, 60).Value = code;
      command.Parameters.Add("@interpretation", SqlDbType.VarChar, 40).Value = InterpretationKind;

      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      if (!await reader.ReadAsync(cancellationToken))
        return null;

      var header = ReadHeader(reader);

      var results = new List<ExperimentResultInfo>();
      string? interpretation = null;
      await reader.NextResultAsync(cancellationToken);
      while (await reader.ReadAsync(cancellationToken))
      {
        var kind = reader.GetString("result_kind");
        results.Add(new ExperimentResultInfo(kind, NullableString(reader, "title"), Convert.ToInt32(reader.GetValue("payload_chars"))));
        if (kind == InterpretationKind)
          interpretation = NullableString(reader, "payload");
      }

      return new ExperimentRecord(header, results, interpretation);
    }

    /// <summary>One result of an experiment: its title and its payload as JSON text. Null when there is none of that kind.</summary>
    public async Task<ExperimentPayload?> GetPayloadAsync(string code, string kind, CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT TOP (1) r.result_kind, r.title, CAST(r.payload AS NVARCHAR(MAX)) AS payload
        FROM dbo.experiment_result AS r
        JOIN dbo.experiment AS e ON e.experiment_id = r.experiment_id
        WHERE e.experiment_code = @code AND r.result_kind = @kind
        ORDER BY r.sort_order, r.result_id;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      command.Parameters.Add("@code", SqlDbType.VarChar, 60).Value = code;
      command.Parameters.Add("@kind", SqlDbType.VarChar, 40).Value = kind;

      await using var reader = await command.ExecuteReaderAsync(cancellationToken);
      if (!await reader.ReadAsync(cancellationToken))
        return null;

      return new ExperimentPayload(reader.GetString("result_kind"), NullableString(reader, "title"), reader.GetString("payload"));
    }

    private static ExperimentHeader ReadHeader(SqlDataReader reader)
    {
      var code = reader.GetString("experiment_code");
      var parameters = NullableString(reader, "parameters");
      var settings = ParseSettings(parameters);

      return new ExperimentHeader(
        Code: code,
        Package: settings.Package ?? PackageOf(code),
        Name: reader.GetString("name"),
        Method: reader.GetString("method"),
        Role: settings.Role,
        Datasets: settings.Datasets,
        IndependentSources: settings.IndependentSources,
        RunAt: reader.IsDBNull("run_at") ? null : reader.GetDateTime("run_at"),
        Subjects: NullableInt(reader, "n_subjects"),
        Variables: NullableInt(reader, "n_variables"),
        Tests: NullableInt(reader, "n_tests"),
        Description: NullableString(reader, "description"),
        Summary: NullableString(reader, "summary"),
        Parameters: parameters);
    }

    /// <summary>The package of a code: <c>SV-01</c> for <c>SV-01-02-ds03-geometry</c>.</summary>
    public static string PackageOf(string code)
    {
      var parts = code.Split('-');
      return parts.Length >= 2 ? $"{parts[0]}-{parts[1]}" : code;
    }

    /// <summary>
    /// The short form of a code that reports use, <c>SV-01-02</c> for <c>SV-01-02-ds03-geometry</c>:
    /// the package and the two-digit number. Null when the code has no such form.
    /// </summary>
    public static string? ShortCodeOf(string code)
    {
      var parts = code.Split('-');
      return parts.Length > 3 && parts[2].Length == 2 && parts[2].All(char.IsAsciiDigit)
        ? $"{parts[0]}-{parts[1]}-{parts[2]}"
        : null;
    }

    private static (string? Package, string? Role, IReadOnlyList<string> Datasets, IReadOnlyList<string> IndependentSources) ParseSettings(string? parameters)
    {
      if (string.IsNullOrWhiteSpace(parameters))
        return (null, null, [], []);

      try
      {
        using var document = JsonDocument.Parse(parameters);
        var root = document.RootElement;
        if (root.ValueKind != JsonValueKind.Object)
          return (null, null, [], []);

        return (Scalar(root, "package"), Scalar(root, "role"), Strings(root, "datasets"), Strings(root, "independent_sources"));
      }
      catch (JsonException)
      {
        return (null, null, [], []);
      }
    }

    private static string? Scalar(JsonElement root, string name) =>
      root.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.String ? value.GetString() : null;

    private static IReadOnlyList<string> Strings(JsonElement root, string name) =>
      root.TryGetProperty(name, out var value) && value.ValueKind == JsonValueKind.Array
        ? value.EnumerateArray().Where(v => v.ValueKind == JsonValueKind.String).Select(v => v.GetString()!).ToList()
        : [];

    private async Task<SqlConnection> OpenAsync(CancellationToken cancellationToken)
    {
      var connection = new SqlConnection(_appSettingsService.GetAppSettings().Connections.Database);
      await connection.OpenAsync(cancellationToken);
      return connection;
    }

    private static string? NullableString(SqlDataReader reader, string name)
    {
      var ordinal = reader.GetOrdinal(name);
      return reader.IsDBNull(ordinal) ? null : reader.GetString(ordinal);
    }

    private static int? NullableInt(SqlDataReader reader, string name)
    {
      var ordinal = reader.GetOrdinal(name);
      return reader.IsDBNull(ordinal) ? null : Convert.ToInt32(reader.GetValue(ordinal));
    }
  }

  /// <summary>One <c>dbo.experiment</c> row.</summary>
  /// <param name="Package">The experiment package, e.g. SV-01: several experiments answer one package's question.</param>
  /// <param name="Role">primary, replication, sensitivity or descriptive (from <c>parameters</c>).</param>
  /// <param name="Datasets">The dataset codes the run used (from <c>parameters</c>).</param>
  /// <param name="Description">The question and the hypothesis.</param>
  /// <param name="Summary">The primary result with its effect size, interval and n.</param>
  /// <param name="Parameters">The run's settings as JSON text, verbatim.</param>
  public sealed record ExperimentHeader(
    string Code, string Package, string Name, string Method, string? Role,
    IReadOnlyList<string> Datasets, IReadOnlyList<string> IndependentSources,
    DateTime? RunAt, int? Subjects, int? Variables, int? Tests,
    string? Description, string? Summary, string? Parameters);

  /// <summary>One result of an experiment, without its payload.</summary>
  public sealed record ExperimentResultInfo(string Kind, string? Title, int Chars);

  public sealed record ExperimentRecord(
    ExperimentHeader Header, IReadOnlyList<ExperimentResultInfo> Results, string? Interpretation);

  public sealed record ExperimentPayload(string Kind, string? Title, string Json);
}
