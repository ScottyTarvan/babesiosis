using System.Data;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Data.SqlClient;
using Out = System.Console;
using static Babesiosis.Console.DatasetLoader;

namespace Babesiosis.Console
{
  /// <summary>
  /// Loads experiment load files (/experiments/&lt;package&gt;/out/db/&lt;code&gt;.json, see /experiments/run-instructions.md) into
  /// dbo.experiment, dbo.association, dbo.cluster_assignment and dbo.experiment_result. Runs after
  /// <see cref="DatasetLoader"/>: variables and subjects are resolved by code within the experiment's dataset.
  /// One transaction per experiment; the experiment row is merged by code and its child rows are replaced.
  /// </summary>
  internal sealed class ExperimentLoader(LoaderSettings settings, LoaderOptions options)
  {
    private readonly List<string> _errors = [];
    private readonly List<string> _warnings = [];

    public async Task<int> RunAsync(CancellationToken cancellationToken)
    {
      var folder = settings.ExperimentsRoot;
      Out.WriteLine();
      Out.WriteLine($"Reading experiments from {Path.Combine(folder, "<package>", "out", "db")}");

      if (!Directory.Exists(folder))
      {
        _warnings.Add($"Folder {folder} not found. Nothing loaded.");
        PrintReport(0, 0, 0, 0);
        return 0;
      }

      // One load file per experiment: <root>/<package>/out/db/<code>.json (see /experiments/run-instructions.md).
      var files = Directory.GetDirectories(folder)
        .Select(package => Path.Combine(package, "out", "db"))
        .Where(Directory.Exists)
        .SelectMany(db => Directory.GetFiles(db, "*.json"))
        .OrderBy(f => f, StringComparer.OrdinalIgnoreCase)
        .ToList();
      var seen = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
      int experiments = 0, associations = 0, clusters = 0, results = 0;

      foreach (var file in files)
      {
        cancellationToken.ThrowIfCancellationRequested();
        ExperimentFile exp;
        try
        {
          exp = JsonSerializer.Deserialize<ExperimentFile>(File.ReadAllText(file), TidyJson.Options)
                ?? throw new InvalidDataException("empty file");
          Validate(exp, file, seen);
        }
        catch (Exception ex) when (ex is JsonException or InvalidDataException)
        {
          _errors.Add($"{Path.GetFileName(file)}: {ex.Message}");
          continue;
        }

        if (options.Only is not null && !options.Only.Contains(exp.Experiment.Code) && !options.Only.Contains(exp.Experiment.Dataset ?? ""))
          continue;

        Out.WriteLine($"  {exp.Experiment.Code}: {exp.Associations.Count} associations, {exp.ClusterAssignments.Count} cluster rows, {exp.Results.Count} results");
        experiments++;
        associations += exp.Associations.Count;
        clusters += exp.ClusterAssignments.Count;
        results += exp.Results.Count;

        if (options.DryRun)
          continue;

        try
        {
          await WriteAsync(exp, cancellationToken);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
          // SqlException, bulk-copy failures and the loader's own consistency checks; the transaction rolled back on disposal.
          _errors.Add($"{exp.Experiment.Code}: {ex.Message}");
        }
      }

      PrintReport(experiments, associations, clusters, results);
      return _errors.Count == 0 ? 0 : 1;
    }

    /// <summary>Checks that would otherwise fail as a null reference or a SQL error, or load one file over another.</summary>
    private static void Validate(ExperimentFile exp, string file, Dictionary<string, string> seen)
    {
      if (exp.Experiment is null || string.IsNullOrWhiteSpace(exp.Experiment.Code))
        throw new InvalidDataException("experiment.code is missing");
      var code = exp.Experiment.Code;
      if (code.Length > 60)
        throw new InvalidDataException($"experiment.code is {code.Length} characters (60 at most)");
      if (!string.Equals(Path.GetFileNameWithoutExtension(file), code, StringComparison.OrdinalIgnoreCase))
        throw new InvalidDataException($"the file name must be {code}.json");
      if (seen.TryGetValue(code, out var other))
        throw new InvalidDataException($"experiment code {code} is also in {other}");
      seen[code] = file;
      if (string.IsNullOrWhiteSpace(exp.Experiment.Name) || string.IsNullOrWhiteSpace(exp.Experiment.Method))
        throw new InvalidDataException("experiment.name and experiment.method are required");
      if (exp.Experiment.Method.Length > 50)
        throw new InvalidDataException("experiment.method is longer than 50 characters");
      if (exp.Associations is null || exp.ClusterAssignments is null || exp.Results is null)
        throw new InvalidDataException("associations, cluster_assignments and results must be present (use [] when empty)");
      if (exp.Experiment.Dataset is null && (exp.Associations.Count > 0 || exp.ClusterAssignments.Count > 0))
        throw new InvalidDataException("associations and cluster_assignments need experiment.dataset");
      foreach (var r in exp.Results)
      {
        if (string.IsNullOrWhiteSpace(r.Kind) || r.Kind.Length > 40)
          throw new InvalidDataException("each result needs a kind of 40 characters at most");
        if (r.Payload.ValueKind is not (JsonValueKind.Object or JsonValueKind.Array))
          throw new InvalidDataException($"result {r.Kind} needs a payload that is an object or an array");
      }
      var repeated = exp.Results.GroupBy(r => r.Kind, StringComparer.Ordinal).FirstOrDefault(g => g.Count() > 1);
      if (repeated is not null)
        throw new InvalidDataException($"result kind {repeated.Key} is used more than once");
    }

    private async Task WriteAsync(ExperimentFile file, CancellationToken cancellationToken)
    {
      await using var connection = new SqlConnection(settings.ConnectionString);
      await connection.OpenAsync(cancellationToken);
      await using var transaction = (SqlTransaction)await connection.BeginTransactionAsync(cancellationToken);

      async Task<object?> Scalar(string sql, params SqlParameter[] parameters)
      {
        await using var command = new SqlCommand(sql, connection, transaction) { CommandTimeout = 300 };
        command.Parameters.AddRange(parameters);
        return await command.ExecuteScalarAsync(cancellationToken);
      }

      async Task Exec(string sql, params SqlParameter[] parameters)
      {
        await using var command = new SqlCommand(sql, connection, transaction) { CommandTimeout = 300 };
        command.Parameters.AddRange(parameters);
        await command.ExecuteNonQueryAsync(cancellationToken);
      }

      async Task Bulk(string table, DataTable data)
      {
        using var bulk = new SqlBulkCopy(connection, SqlBulkCopyOptions.Default, transaction) { DestinationTableName = table, BulkCopyTimeout = 300 };
        foreach (DataColumn column in data.Columns)
          bulk.ColumnMappings.Add(column.ColumnName, column.ColumnName);
        await bulk.WriteToServerAsync(data, cancellationToken);
      }

      var e = file.Experiment;
      object? datasetId = null;
      if (e.Dataset is not null)
      {
        datasetId = await Scalar("SELECT dataset_id FROM dbo.dataset WHERE dataset_code = @code;", P("@code", SqlDbType.VarChar, 20, e.Dataset));
        if (datasetId is null)
          throw new SqlExceptionLike($"dataset {e.Dataset} is not loaded; run the dataset load first.");
      }

      await Exec("""
        MERGE dbo.experiment WITH (HOLDLOCK) AS t
        USING (SELECT @experiment_code AS experiment_code) AS s ON t.experiment_code = s.experiment_code
        WHEN MATCHED THEN UPDATE SET
          name = @name, description = @description, method = @method, dataset_id = @dataset_id, parameters = @parameters, script = @script,
          script_version = @script_version, run_at = @run_at, n_subjects = @n_subjects, n_variables = @n_variables, n_tests = @n_tests,
          summary = @summary, loaded_at = SYSUTCDATETIME()
        WHEN NOT MATCHED BY TARGET THEN
          INSERT (experiment_code, name, description, method, dataset_id, parameters, script, script_version, run_at, n_subjects, n_variables, n_tests, summary)
          VALUES (@experiment_code, @name, @description, @method, @dataset_id, @parameters, @script, @script_version, @run_at, @n_subjects, @n_variables, @n_tests, @summary);
        """,
        P("@experiment_code", SqlDbType.VarChar, 60, e.Code),
        P("@name", SqlDbType.NVarChar, 200, Truncate(e.Name, 200)),
        P("@description", SqlDbType.NVarChar, -1, e.Description),
        P("@method", SqlDbType.VarChar, 50, e.Method),
        P("@dataset_id", SqlDbType.Int, 0, datasetId),
        P("@parameters", SqlDbType.NVarChar, -1, JsonOrNull(e.Parameters) is string s ? s : null),
        P("@script", SqlDbType.NVarChar, 200, e.Script),
        P("@script_version", SqlDbType.VarChar, 64, e.ScriptVersion),
        P("@run_at", SqlDbType.DateTime2, 0, ParseUtc(e.RunUtc)),
        P("@n_subjects", SqlDbType.Int, 0, e.NSubjects),
        P("@n_variables", SqlDbType.Int, 0, e.NVariables),
        P("@n_tests", SqlDbType.Int, 0, e.NTests),
        P("@summary", SqlDbType.NVarChar, -1, e.Summary));

      var experimentId = (int)(await Scalar("SELECT experiment_id FROM dbo.experiment WHERE experiment_code = @code;", P("@code", SqlDbType.VarChar, 60, e.Code)))!;

      await Exec("""
        DELETE FROM dbo.association        WHERE experiment_id = @experiment_id;
        DELETE FROM dbo.cluster_assignment WHERE experiment_id = @experiment_id;
        DELETE FROM dbo.experiment_result  WHERE experiment_id = @experiment_id;
        """, P("@experiment_id", SqlDbType.Int, 0, experimentId));

      // Temp tables are created in a batch without parameters: a parameterised batch runs through sp_executesql,
      // whose temp tables are dropped when it returns.
      await Exec("""
        CREATE TABLE #association (variable_a VARCHAR(60) NOT NULL, variable_b VARCHAR(60) NOT NULL, test VARCHAR(30) NOT NULL, estimate FLOAT NULL,
                                   estimate_label VARCHAR(30) NULL, n INT NOT NULL, p_value FLOAT NULL, p_adjusted FLOAT NULL, significant BIT NOT NULL,
                                   trivial BIT NOT NULL, direction NVARCHAR(200) NULL, detail NVARCHAR(MAX) NULL);
        CREATE TABLE #cluster (subject_code VARCHAR(60) NOT NULL, cluster_label VARCHAR(30) NOT NULL, score FLOAT NULL);
        """);

      var associationTable = new DataTable();
      foreach (var (name, type) in new[] { ("variable_a", typeof(string)), ("variable_b", typeof(string)), ("test", typeof(string)), ("estimate", typeof(double)),
                 ("estimate_label", typeof(string)), ("n", typeof(int)), ("p_value", typeof(double)), ("p_adjusted", typeof(double)), ("significant", typeof(bool)),
                 ("trivial", typeof(bool)), ("direction", typeof(string)), ("detail", typeof(string)) })
        associationTable.Columns.Add(name, type);
      foreach (var a in file.Associations)
        associationTable.Rows.Add(a.VariableA, a.VariableB, a.Test, Null(a.Estimate), Null(a.EstimateLabel), a.N, Null(a.PValue), Null(a.PAdjusted),
          a.Significant, a.Trivial, Null(Truncate(a.Direction, 200)), JsonOrNull(a.Detail));

      var clusterTable = new DataTable();
      clusterTable.Columns.Add("subject_code", typeof(string));
      clusterTable.Columns.Add("cluster_label", typeof(string));
      clusterTable.Columns.Add("score", typeof(double));
      foreach (var c in file.ClusterAssignments)
        clusterTable.Rows.Add(c.Subject, c.Cluster, Null(c.Score));

      await Bulk("#association", associationTable);
      await Bulk("#cluster", clusterTable);

      var unresolved = await Scalar("""
        SELECT COUNT(*) FROM #association AS a
        WHERE NOT EXISTS (SELECT 1 FROM dbo.variable WHERE dataset_id = @dataset_id AND variable_code = a.variable_a)
           OR NOT EXISTS (SELECT 1 FROM dbo.variable WHERE dataset_id = @dataset_id AND variable_code = a.variable_b);
        """, P("@dataset_id", SqlDbType.Int, 0, datasetId));
      if (unresolved is int u && u > 0)
        throw new SqlExceptionLike($"{u} associations name variables that are not in dataset {e.Dataset}; reload the dataset first.");

      await Exec("""
        INSERT INTO dbo.association (experiment_id, variable_a_id, variable_b_id, test, estimate, estimate_label, n, p_value, p_adjusted, significant, trivial, direction, detail)
        SELECT @experiment_id, va.variable_id, vb.variable_id, a.test, a.estimate, a.estimate_label, a.n, a.p_value, a.p_adjusted, a.significant, a.trivial, a.direction, a.detail
        FROM #association AS a
        JOIN dbo.variable AS va ON va.dataset_id = @dataset_id AND va.variable_code = a.variable_a
        JOIN dbo.variable AS vb ON vb.dataset_id = @dataset_id AND vb.variable_code = a.variable_b;

        INSERT INTO dbo.cluster_assignment (experiment_id, subject_id, cluster_label, score)
        SELECT @experiment_id, s.subject_id, c.cluster_label, c.score
        FROM #cluster AS c
        JOIN dbo.subject AS s ON s.dataset_id = @dataset_id AND s.subject_code = c.subject_code;
        """, P("@experiment_id", SqlDbType.Int, 0, experimentId), P("@dataset_id", SqlDbType.Int, 0, datasetId));

      foreach (var r in file.Results)
        await Exec("INSERT INTO dbo.experiment_result (experiment_id, result_kind, title, payload, sort_order) VALUES (@experiment_id, @kind, @title, @payload, @sort_order);",
          P("@experiment_id", SqlDbType.Int, 0, experimentId),
          P("@kind", SqlDbType.VarChar, 40, r.Kind),
          P("@title", SqlDbType.NVarChar, 200, Truncate(r.Title, 200)),
          P("@payload", SqlDbType.NVarChar, -1, r.Payload.GetRawText()),
          P("@sort_order", SqlDbType.SmallInt, 0, (short)r.SortOrder));

      await transaction.CommitAsync(cancellationToken);
    }

    private void PrintReport(int experiments, int associations, int clusters, int results)
    {
      Out.WriteLine();
      Out.WriteLine(options.DryRun ? "Experiments dry run (nothing written)" : "Experiments load summary");
      static void Row(string label, int value) => Out.WriteLine($"  {(label + ":").PadRight(34)}{value}");
      Row("Experiments", experiments);
      Row("Associations", associations);
      Row("Cluster assignments", clusters);
      Row("Result payloads", results);
      Row("Warnings", _warnings.Count);
      Row("Errors", _errors.Count);
      foreach (var w in _warnings) Out.WriteLine($"  warning: {w}");
      foreach (var e in _errors) Out.WriteLine($"  error: {e}");
    }
  }

  /// <summary>A load-time consistency failure, reported like a SQL error (the transaction is rolled back by disposal).</summary>
  internal sealed class SqlExceptionLike(string message) : Exception(message);

  internal sealed record ExperimentFile(ExperimentHeader Experiment, List<AssociationRow> Associations,
    [property: JsonPropertyName("cluster_assignments")] List<ClusterRow> ClusterAssignments, List<ResultRow> Results);

  internal sealed record ExperimentHeader(string Code, string Name, string? Description, string Method, string? Dataset, JsonElement Parameters,
    string? Script, [property: JsonPropertyName("script_version")] string? ScriptVersion, [property: JsonPropertyName("run_utc")] string? RunUtc,
    [property: JsonPropertyName("n_subjects")] int? NSubjects, [property: JsonPropertyName("n_variables")] int? NVariables,
    [property: JsonPropertyName("n_tests")] int? NTests, string? Summary);

  internal sealed record AssociationRow([property: JsonPropertyName("variable_a")] string VariableA, [property: JsonPropertyName("variable_b")] string VariableB,
    string Test, double? Estimate, [property: JsonPropertyName("estimate_label")] string? EstimateLabel, int N,
    [property: JsonPropertyName("p_value")] double? PValue, [property: JsonPropertyName("p_adjusted")] double? PAdjusted,
    bool Significant, bool Trivial, string? Direction, JsonElement Detail);

  internal sealed record ClusterRow([property: JsonPropertyName("subject_code")] string Subject,
    [property: JsonPropertyName("cluster_label")] string Cluster, double? Score);

  internal sealed record ResultRow(string Kind, string? Title, JsonElement Payload, [property: JsonPropertyName("sort_order")] int SortOrder);
}
