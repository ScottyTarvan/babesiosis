using System.Data;
using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Data.SqlClient;
using Out = System.Console;

namespace Babesiosis.Console
{
  /// <summary>
  /// Loads the tidy dataset files (core/data/tidy/&lt;DS&gt;.json, written by scripts/tidy_*.py) into
  /// dbo.dataset, dbo.variable, dbo.subject and dbo.observation. One transaction per dataset: the
  /// dataset, variables and subjects are merged by code, the observations are replaced.
  /// </summary>
  internal sealed class DatasetLoader(LoaderSettings settings, LoaderOptions options)
  {
    private readonly List<string> _errors = [];
    private readonly List<string> _warnings = [];

    public async Task<int> RunAsync(CancellationToken cancellationToken)
    {
      var folder = Path.Combine(settings.ReviewRoot, "data", "tidy");
      Out.WriteLine();
      Out.WriteLine($"Reading tidy datasets from {folder}");

      if (!Directory.Exists(folder))
      {
        _warnings.Add($"Folder {folder} not found. Run a scripts/tidy_*.py script first. Nothing loaded.");
        PrintReport(0, 0, 0, 0);
        return 0;
      }

      var files = Directory.GetFiles(folder, "*.json").OrderBy(f => f, StringComparer.OrdinalIgnoreCase).ToList();
      int datasets = 0, variables = 0, subjects = 0, observations = 0;

      foreach (var file in files)
      {
        cancellationToken.ThrowIfCancellationRequested();
        TidyFile tidy;
        try
        {
          tidy = JsonSerializer.Deserialize<TidyFile>(File.ReadAllText(file), TidyJson.Options)
                 ?? throw new InvalidDataException("empty file");
          Validate(tidy, file);
        }
        catch (Exception ex) when (ex is JsonException or InvalidDataException)
        {
          _errors.Add($"{Path.GetFileName(file)}: {ex.Message}");
          continue;
        }

        if (options.Only is not null && !options.Only.Contains(tidy.Dataset.Code))
          continue;

        Out.WriteLine($"  {tidy.Dataset.Code}: {tidy.Subjects.Count} subjects, {tidy.Variables.Count} variables, {tidy.Observations.Count} observations");
        datasets++;
        variables += tidy.Variables.Count;
        subjects += tidy.Subjects.Count;
        observations += tidy.Observations.Count;

        if (options.DryRun)
          continue;

        try
        {
          await WriteAsync(tidy, cancellationToken);
        }
        catch (Exception ex) when (ex is not OperationCanceledException)
        {
          // SqlException and bulk-copy failures; the transaction rolled back on disposal.
          _errors.Add($"{tidy.Dataset.Code}: {ex.Message}");
        }
      }

      PrintReport(datasets, variables, subjects, observations);
      return _errors.Count == 0 ? 0 : 1;
    }

    private void Validate(TidyFile tidy, string file)
    {
      if (string.IsNullOrWhiteSpace(tidy.Dataset.Code))
        throw new InvalidDataException("dataset.code is missing");
      var variableCodes = tidy.Variables.Select(v => v.Code).ToHashSet(StringComparer.Ordinal);
      var subjectCodes = tidy.Subjects.Select(s => s.Code).ToHashSet(StringComparer.Ordinal);
      if (variableCodes.Count != tidy.Variables.Count)
        throw new InvalidDataException("duplicate variable codes");
      if (subjectCodes.Count != tidy.Subjects.Count)
        throw new InvalidDataException("duplicate subject codes");
      var orphans = tidy.Observations.Count(o => !variableCodes.Contains(o.Variable) || !subjectCodes.Contains(o.Subject));
      if (orphans > 0)
        throw new InvalidDataException($"{orphans} observations name a subject or variable that is not declared");
      foreach (var v in tidy.Variables.Where(v => v.DataType is not ("N" or "O" or "C" or "D" or "T")))
        throw new InvalidDataException($"variable {v.Code} has data_type '{v.DataType}' (expected N, O, C, D or T)");
      if (tidy.Dataset.ArticleCode is null)
        _warnings.Add($"{Path.GetFileName(file)}: no article_code; the dataset will not link to an article.");
    }

    private async Task WriteAsync(TidyFile tidy, CancellationToken cancellationToken)
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

      var d = tidy.Dataset;
      var articleId = d.ArticleCode is null
        ? null
        : await Scalar("SELECT article_id FROM dbo.article WHERE article_code = @code;", P("@code", SqlDbType.VarChar, 10, d.ArticleCode));
      if (d.ArticleCode is not null && articleId is null)
        _warnings.Add($"{d.Code}: article {d.ArticleCode} is not in dbo.article; article_id left NULL.");

      // Dataset row, merged by code
      await Exec("""
        MERGE dbo.dataset WITH (HOLDLOCK) AS t
        USING (SELECT @dataset_code AS dataset_code) AS s ON t.dataset_code = s.dataset_code
        WHEN MATCHED THEN UPDATE SET
          title = @title, article_code = @article_code, article_id = @article_id, repository = @repository,
          source_record = @source_record, licence = @licence, independent_source = @independent_source, species = @species,
          design = @design, source_file = @source_file, source_sha256 = @source_sha256, notes = @notes, extracted_at = @extracted_at,
          loaded_at = SYSUTCDATETIME()
        WHEN NOT MATCHED BY TARGET THEN
          INSERT (dataset_code, title, article_code, article_id, repository, source_record, licence, independent_source, species,
                  design, source_file, source_sha256, notes, extracted_at)
          VALUES (@dataset_code, @title, @article_code, @article_id, @repository, @source_record, @licence, @independent_source, @species,
                  @design, @source_file, @source_sha256, @notes, @extracted_at);
        """,
        P("@dataset_code", SqlDbType.VarChar, 20, d.Code),
        P("@title", SqlDbType.NVarChar, 500, Truncate(d.Title, 500)),
        P("@article_code", SqlDbType.VarChar, 10, d.ArticleCode),
        P("@article_id", SqlDbType.Int, 0, articleId),
        P("@repository", SqlDbType.NVarChar, 200, Truncate(d.Repository, 200)),
        P("@source_record", SqlDbType.NVarChar, 400, Truncate(d.SourceRecord, 400)),
        P("@licence", SqlDbType.NVarChar, 400, Truncate(d.Licence, 400)),
        P("@independent_source", SqlDbType.VarChar, 10, d.IndependentSource),
        P("@species", SqlDbType.NVarChar, 400, Truncate(d.Species, 400)),
        P("@design", SqlDbType.NVarChar, -1, d.Design),
        P("@source_file", SqlDbType.NVarChar, 300, d.SourceFile),
        P("@source_sha256", SqlDbType.Char, 64, d.SourceSha256),
        P("@notes", SqlDbType.NVarChar, -1, d.Notes is null ? null : JsonSerializer.Serialize(d.Notes)),
        P("@extracted_at", SqlDbType.DateTime2, 0, ParseUtc(d.ExtractedUtc)));

      var datasetId = (int)(await Scalar("SELECT dataset_id FROM dbo.dataset WHERE dataset_code = @code;", P("@code", SqlDbType.VarChar, 20, d.Code)))!;
      var idParam = () => P("@dataset_id", SqlDbType.Int, 0, datasetId);

      // Variables and subjects through temp tables, merged by code
      await Exec("""
        CREATE TABLE #variable (variable_code VARCHAR(60) NOT NULL PRIMARY KEY, name NVARCHAR(200) NOT NULL, source_name NVARCHAR(200) NULL,
                                unit NVARCHAR(50) NULL, data_type CHAR(1) NOT NULL, domain VARCHAR(30) NULL, derived BIT NOT NULL,
                                derived_from NVARCHAR(MAX) NULL, include_default BIT NOT NULL, ref_low FLOAT NULL, ref_high FLOAT NULL,
                                description NVARCHAR(1000) NULL, levels NVARCHAR(MAX) NULL, sort_order SMALLINT NOT NULL);
        CREATE TABLE #subject (subject_code VARCHAR(60) NOT NULL PRIMARY KEY, group_label NVARCHAR(100) NULL, outcome_label NVARCHAR(100) NULL);
        CREATE TABLE #observation (subject_code VARCHAR(60) NOT NULL, variable_code VARCHAR(60) NOT NULL, time_point VARCHAR(30) NOT NULL,
                                   value_num FLOAT NULL, value_text NVARCHAR(400) NULL, value_date DATE NULL,
                                   PRIMARY KEY (subject_code, variable_code, time_point));
        """);

      var variableTable = new DataTable();
      foreach (var (name, type) in new[] { ("variable_code", typeof(string)), ("name", typeof(string)), ("source_name", typeof(string)),
                 ("unit", typeof(string)), ("data_type", typeof(string)), ("domain", typeof(string)), ("derived", typeof(bool)),
                 ("derived_from", typeof(string)), ("include_default", typeof(bool)), ("ref_low", typeof(double)), ("ref_high", typeof(double)),
                 ("description", typeof(string)), ("levels", typeof(string)), ("sort_order", typeof(short)) })
        variableTable.Columns.Add(name, type);
      foreach (var v in tidy.Variables)
        variableTable.Rows.Add(v.Code, Truncate(v.Name, 200), Null(Truncate(v.SourceName, 200)), Null(v.Unit), v.DataType, Null(v.Domain), v.Derived,
          JsonOrNull(v.DerivedFrom), v.IncludeDefault, Null(v.RefLow), Null(v.RefHigh), Null(Truncate(v.Description, 1000)), JsonOrNull(v.Levels),
          (short)v.SortOrder);

      var subjectTable = new DataTable();
      subjectTable.Columns.Add("subject_code", typeof(string));
      subjectTable.Columns.Add("group_label", typeof(string));
      subjectTable.Columns.Add("outcome_label", typeof(string));
      foreach (var s in tidy.Subjects)
        subjectTable.Rows.Add(s.Code, Null(Truncate(s.GroupLabel, 100)), Null(Truncate(s.OutcomeLabel, 100)));

      var observationTable = new DataTable();
      observationTable.Columns.Add("subject_code", typeof(string));
      observationTable.Columns.Add("variable_code", typeof(string));
      observationTable.Columns.Add("time_point", typeof(string));
      observationTable.Columns.Add("value_num", typeof(double));
      observationTable.Columns.Add("value_text", typeof(string));
      observationTable.Columns.Add("value_date", typeof(DateTime));
      foreach (var o in tidy.Observations)
        observationTable.Rows.Add(o.Subject, o.Variable, o.TimePoint ?? "", Null(o.ValueNum), Null(Truncate(o.ValueText, 400)),
          o.ValueDate is null ? DBNull.Value : DateTime.ParseExact(o.ValueDate, "yyyy-MM-dd", CultureInfo.InvariantCulture));

      await Bulk("#variable", variableTable);
      await Bulk("#subject", subjectTable);
      await Bulk("#observation", observationTable);

      await Exec("""
        MERGE dbo.variable WITH (HOLDLOCK) AS t
        USING #variable AS s ON t.dataset_id = @dataset_id AND t.variable_code = s.variable_code
        WHEN MATCHED THEN UPDATE SET
          name = s.name, source_name = s.source_name, unit = s.unit, data_type = s.data_type, domain = s.domain, derived = s.derived,
          derived_from = s.derived_from, include_default = s.include_default, ref_low = s.ref_low, ref_high = s.ref_high,
          description = s.description, levels = s.levels, sort_order = s.sort_order
        WHEN NOT MATCHED BY TARGET THEN
          INSERT (dataset_id, variable_code, name, source_name, unit, data_type, domain, derived, derived_from, include_default,
                  ref_low, ref_high, description, levels, sort_order)
          VALUES (@dataset_id, s.variable_code, s.name, s.source_name, s.unit, s.data_type, s.domain, s.derived, s.derived_from, s.include_default,
                  s.ref_low, s.ref_high, s.description, s.levels, s.sort_order);

        MERGE dbo.subject WITH (HOLDLOCK) AS t
        USING #subject AS s ON t.dataset_id = @dataset_id AND t.subject_code = s.subject_code
        WHEN MATCHED THEN UPDATE SET group_label = s.group_label, outcome_label = s.outcome_label
        WHEN NOT MATCHED BY TARGET THEN
          INSERT (dataset_id, subject_code, group_label, outcome_label) VALUES (@dataset_id, s.subject_code, s.group_label, s.outcome_label);

        DELETE o FROM dbo.observation AS o JOIN dbo.subject AS s ON s.subject_id = o.subject_id WHERE s.dataset_id = @dataset_id;

        INSERT INTO dbo.observation (subject_id, variable_id, time_point, value_num, value_text, value_date)
        SELECT s.subject_id, v.variable_id, o.time_point, o.value_num, o.value_text, o.value_date
        FROM #observation AS o
        JOIN dbo.subject  AS s ON s.dataset_id = @dataset_id AND s.subject_code = o.subject_code
        JOIN dbo.variable AS v ON v.dataset_id = @dataset_id AND v.variable_code = o.variable_code;

        UPDATE dbo.dataset SET n_subjects = (SELECT COUNT(*) FROM dbo.subject WHERE dataset_id = @dataset_id) WHERE dataset_id = @dataset_id;
        """, idParam());

      // Variables and subjects that are in the database but no longer in the file are kept (experiments may reference them) and reported.
      var stale = await Scalar("""
        SELECT COUNT(*) FROM dbo.variable AS v WHERE v.dataset_id = @dataset_id AND NOT EXISTS (SELECT 1 FROM #variable AS s WHERE s.variable_code = v.variable_code);
        """, idParam());
      if (stale is int n && n > 0)
        _warnings.Add($"{d.Code}: {n} variables in dbo.variable are no longer in the tidy file; they were kept.");

      await transaction.CommitAsync(cancellationToken);
    }

    // ---------------------------------------------------------------------------------------------------------

    private void PrintReport(int datasets, int variables, int subjects, int observations)
    {
      Out.WriteLine();
      Out.WriteLine(options.DryRun ? "Datasets dry run (nothing written)" : "Datasets load summary");
      static void Row(string label, int value) => Out.WriteLine($"  {(label + ":").PadRight(34)}{value}");
      Row("Datasets", datasets);
      Row("Variables", variables);
      Row("Subjects", subjects);
      Row("Observations", observations);
      Row("Warnings", _warnings.Count);
      Row("Errors", _errors.Count);
      foreach (var w in _warnings) Out.WriteLine($"  warning: {w}");
      foreach (var e in _errors) Out.WriteLine($"  error: {e}");
    }

    internal static SqlParameter P(string name, SqlDbType type, int size, object? value)
    {
      var p = size == 0 ? new SqlParameter(name, type) : new SqlParameter(name, type, size);
      p.Value = value ?? DBNull.Value;
      return p;
    }

    internal static object Null(object? value) => value ?? DBNull.Value;

    internal static string? Truncate(string? value, int max) => value is null ? null : value.Length <= max ? value : value[..max];

    internal static object JsonOrNull(JsonElement element) =>
      element.ValueKind is JsonValueKind.Undefined or JsonValueKind.Null ? DBNull.Value : element.GetRawText();

    internal static object ParseUtc(string? iso) =>
      iso is null ? DBNull.Value : DateTimeOffset.Parse(iso, CultureInfo.InvariantCulture).UtcDateTime;
  }

  internal static class TidyJson
  {
    public static readonly JsonSerializerOptions Options = new()
    {
      PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
      PropertyNameCaseInsensitive = true,
      NumberHandling = JsonNumberHandling.AllowReadingFromString
    };
  }

  internal sealed record TidyFile(TidyDataset Dataset, List<TidyVariable> Variables, List<TidySubject> Subjects, List<TidyObservation> Observations);

  internal sealed record TidyDataset(
    string Code, string Title, [property: JsonPropertyName("article_code")] string? ArticleCode, string? Repository,
    [property: JsonPropertyName("source_record")] string? SourceRecord, string? Licence,
    [property: JsonPropertyName("independent_source")] string? IndependentSource, string? Species, string? Design,
    [property: JsonPropertyName("source_file")] string? SourceFile, [property: JsonPropertyName("source_sha256")] string? SourceSha256,
    [property: JsonPropertyName("n_subjects")] int NSubjects, List<string>? Notes,
    [property: JsonPropertyName("extracted_utc")] string? ExtractedUtc, string? Script);

  internal sealed record TidyVariable(
    string Code, string Name, [property: JsonPropertyName("source_name")] string? SourceName, string? Unit,
    [property: JsonPropertyName("data_type")] string DataType, string? Domain, bool Derived,
    [property: JsonPropertyName("derived_from")] JsonElement DerivedFrom, [property: JsonPropertyName("include_default")] bool IncludeDefault,
    [property: JsonPropertyName("ref_low")] double? RefLow, [property: JsonPropertyName("ref_high")] double? RefHigh,
    string? Description, JsonElement Levels, [property: JsonPropertyName("sort_order")] int SortOrder);

  internal sealed record TidySubject(string Code, [property: JsonPropertyName("group_label")] string? GroupLabel,
    [property: JsonPropertyName("outcome_label")] string? OutcomeLabel);

  internal sealed record TidyObservation(string Subject, string Variable, [property: JsonPropertyName("time_point")] string? TimePoint,
    [property: JsonPropertyName("value_num")] double? ValueNum, [property: JsonPropertyName("value_text")] string? ValueText,
    [property: JsonPropertyName("value_date")] string? ValueDate);
}
