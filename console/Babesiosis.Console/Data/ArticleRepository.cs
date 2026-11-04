using System.Data;
using System.Text;
using Babesiosis.Console.Source;
using Microsoft.Data;
using Microsoft.Data.SqlClient;
using Microsoft.Data.SqlTypes;

namespace Babesiosis.Console.Data
{
  /// <summary>What to do with an existing row's embedding columns.</summary>
  internal enum EmbeddingAction
  {
    /// <summary>Leave the stored vector as it is (text unchanged, or embeddings skipped for a new row).</summary>
    Keep,
    /// <summary>Store a newly generated vector.</summary>
    Set,
    /// <summary>The text changed but no vector was generated: clear the stale one so the next run embeds it.</summary>
    Clear
  }

  internal sealed record ExistingArticle(byte[] ContentHash, bool HasEmbedding);

  internal sealed record TagRow(int CategoryId, string TagType);

  internal sealed class ArticleRepository(string connectionString, int dimensions)
  {
    public async Task<bool> SchemaExistsAsync(CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT CASE WHEN OBJECT_ID(N'dbo.category', N'U') IS NOT NULL
                     AND OBJECT_ID(N'dbo.article', N'U') IS NOT NULL
                     AND OBJECT_ID(N'dbo.article_category', N'U') IS NOT NULL
                    THEN 1 ELSE 0 END;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      return (int)(await command.ExecuteScalarAsync(cancellationToken))! == 1;
    }

    /// <summary>Maps category_code to category_id.</summary>
    public async Task<Dictionary<string, int>> GetCategoryIdsAsync(CancellationToken cancellationToken)
    {
      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand("SELECT category_code, category_id FROM dbo.category;", connection);
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);

      var ids = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);
      while (await reader.ReadAsync(cancellationToken))
        ids[reader.GetString(0).Trim()] = reader.GetInt32(1);
      return ids;
    }

    /// <summary>Maps article_code to the stored content hash and whether a vector is present.</summary>
    public async Task<Dictionary<string, ExistingArticle>> GetExistingAsync(CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT article_code, content_hash, CAST(CASE WHEN embedding IS NULL THEN 0 ELSE 1 END AS BIT)
        FROM dbo.article;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);

      var existing = new Dictionary<string, ExistingArticle>(StringComparer.OrdinalIgnoreCase);
      while (await reader.ReadAsync(cancellationToken))
        existing[reader.GetString(0)] = new ExistingArticle((byte[])reader[1], reader.GetBoolean(2));
      return existing;
    }

    /// <summary>
    /// Inserts or updates one article and replaces its article_category rows, in one transaction.
    /// Returns true when the row was inserted.
    /// </summary>
    public async Task<bool> UpsertAsync(
      ArticleItem item,
      int? primaryCategoryId,
      IReadOnlyList<TagRow> tags,
      EmbeddingAction embeddingAction,
      float[]? embedding,
      string embeddingModel,
      CancellationToken cancellationToken)
    {
      var columns = ArticleColumns(item, primaryCategoryId);

      await using var connection = await OpenAsync(cancellationToken);
      await using var transaction = (SqlTransaction)await connection.BeginTransactionAsync(cancellationToken);

      bool inserted;
      int articleId;
      await using (var merge = new SqlCommand(BuildMergeSql(columns), connection, transaction))
      {
        foreach (var (name, type, size, value) in columns)
          merge.Parameters.Add(new SqlParameter("@" + name, type, size) { Value = value ?? DBNull.Value });

        merge.Parameters.Add(new SqlParameter("@embedding_action", SqlDbType.VarChar, 5) { Value = embeddingAction.ToString().ToLowerInvariant() });
        merge.Parameters.Add(new SqlParameter("@embedding", SqlDbTypeExtensions.Vector)
        {
          Value = embedding is null ? SqlVector<float>.CreateNull(dimensions) : new SqlVector<float>(embedding)
        });
        merge.Parameters.Add(new SqlParameter("@embedding_model", SqlDbType.VarChar, 100) { Value = embeddingModel });

        await using var reader = await merge.ExecuteReaderAsync(cancellationToken);
        await reader.ReadAsync(cancellationToken);
        inserted = reader.GetString(0) == "INSERT";
        articleId = reader.GetInt32(1);
      }

      var tagSql = new StringBuilder("DELETE FROM dbo.article_category WHERE article_id = @article_id;");
      if (tags.Count > 0)
      {
        tagSql.Append("\nINSERT INTO dbo.article_category (article_id, category_id, tag_type) VALUES ");
        tagSql.AppendJoin(", ", tags.Select((_, i) => $"(@article_id, @category_id{i}, @tag_type{i})"));
        tagSql.Append(';');
      }

      await using (var tagCommand = new SqlCommand(tagSql.ToString(), connection, transaction))
      {
        tagCommand.Parameters.Add(new SqlParameter("@article_id", SqlDbType.Int) { Value = articleId });
        for (var i = 0; i < tags.Count; i++)
        {
          tagCommand.Parameters.Add(new SqlParameter($"@category_id{i}", SqlDbType.Int) { Value = tags[i].CategoryId });
          tagCommand.Parameters.Add(new SqlParameter($"@tag_type{i}", SqlDbType.VarChar, 10) { Value = tags[i].TagType });
        }
        await tagCommand.ExecuteNonQueryAsync(cancellationToken);
      }

      await transaction.CommitAsync(cancellationToken);
      return inserted;
    }

    /// <summary>
    /// Column values for one article. Strings are sent as NVARCHAR(MAX) so that a value too long
    /// for its column fails with a truncation error instead of being cut silently by the client.
    /// </summary>
    private static List<(string Name, SqlDbType Type, int Size, object? Value)> ArticleColumns(ArticleItem item, int? primaryCategoryId)
    {
      const int Max = -1;
      var r = item.Record;
      var s = item.Sections;
      var (pubDate, precision) = ArticleSource.ParsePublicationDate(r.FirstPubDate);

      return
      [
        ("article_code", SqlDbType.NVarChar, Max, r.Id),
        ("source_key", SqlDbType.NVarChar, Max, r.Key),
        ("file_name", SqlDbType.NVarChar, Max, Path.GetFileName(r.Filename)),
        ("title", SqlDbType.NVarChar, Max, r.Title),
        ("authors", SqlDbType.NVarChar, Max, r.Authors is { Count: > 0 } ? string.Join(", ", r.Authors) : null),
        ("journal", SqlDbType.NVarChar, Max, r.Journal),
        ("volume_issue_pages", SqlDbType.NVarChar, Max, r.VolumeIssuePages),
        ("doi", SqlDbType.NVarChar, Max, r.Doi),
        ("pmid", SqlDbType.NVarChar, Max, r.Pmid),
        ("pmcid", SqlDbType.NVarChar, Max, r.Pmcid),
        ("language", SqlDbType.NVarChar, Max, r.Language),
        ("corrections", SqlDbType.NVarChar, Max, r.Corrections),
        ("pub_date", SqlDbType.Date, 0, pubDate),
        ("pub_date_precision", SqlDbType.NVarChar, Max, precision?.ToString()),
        ("pub_year", SqlDbType.SmallInt, 0, pubDate is { } d ? (short)d.Year : null),
        ("first_pub_date_text", SqlDbType.NVarChar, Max, r.FirstPubDate),
        ("online_date_text", SqlDbType.NVarChar, Max, r.OnlineDate),
        ("issue_date_text", SqlDbType.NVarChar, Max, r.IssueDate),
        ("date_note", SqlDbType.NVarChar, Max, r.DateNote),
        ("scope_label", SqlDbType.NVarChar, Max, r.ScopeLabel),
        ("include_type", SqlDbType.NVarChar, Max, r.IncludeType),
        ("study_type", SqlDbType.NVarChar, Max, r.StudyType),
        ("older_foundational", SqlDbType.Bit, 0, r.OlderFoundational),
        ("design", SqlDbType.NVarChar, Max, r.Design),
        ("evidence_type", SqlDbType.NVarChar, Max, r.EvidenceType),
        ("host", SqlDbType.NVarChar, Max, r.Host),
        ("country", SqlDbType.NVarChar, Max, r.Country),
        ("species_summary", SqlDbType.NVarChar, Max, r.SpeciesShort),
        ("species", SqlDbType.NVarChar, Max, ArticleRecord.RawJson(r.Species)),
        ("sample_size", SqlDbType.NVarChar, Max, r.SampleSize),
        ("n_infected_dogs", SqlDbType.Int, 0, r.NInfectedDogs),
        ("n_controls", SqlDbType.Int, 0, r.NControls),
        ("cohort_id", SqlDbType.NVarChar, Max, r.CohortId),
        ("primary_category_id", SqlDbType.Int, 0, primaryCategoryId),
        ("one_sentence_finding", SqlDbType.NVarChar, Max, r.OneSentenceFinding),
        ("abstract_summary", SqlDbType.NVarChar, Max, s.AbstractSummary),
        ("authors_conclusion", SqlDbType.NVarChar, Max, s.AuthorsConclusion),
        ("reviewer_interpretation", SqlDbType.NVarChar, Max, s.ReviewerInterpretation),
        ("key_limitations", SqlDbType.NVarChar, Max, s.KeyLimitations),
        ("relevance", SqlDbType.NVarChar, Max, s.Relevance),
        ("evidence_basis", SqlDbType.NVarChar, Max, s.EvidenceBasis),
        ("markdown", SqlDbType.NVarChar, Max, item.Markdown),
        ("abstract_available", SqlDbType.Bit, 0, r.AbstractAvailable),
        ("abstract_source", SqlDbType.NVarChar, Max, r.AbstractSource),
        ("fulltext_checked", SqlDbType.Bit, 0, r.FulltextChecked),
        ("fulltext_url", SqlDbType.NVarChar, Max, r.FulltextUrl),
        ("supplement_checked", SqlDbType.Bit, 0, r.SupplementChecked),
        ("repository_checked", SqlDbType.Bit, 0, r.RepositoryChecked),
        ("data_availability_statement", SqlDbType.NVarChar, Max, r.DataAvailabilityStatement),
        ("dataset_status_code", SqlDbType.TinyInt, 0, r.DatasetStatusCode is { } code ? (byte)code : null),
        ("dataset_status", SqlDbType.NVarChar, Max, r.DatasetStatus),
        ("dataset_ids", SqlDbType.NVarChar, Max, ArticleRecord.RawJson(r.DatasetIds)),
        ("source_links", SqlDbType.NVarChar, Max, ArticleRecord.RawJson(r.SourceLinks)),
        ("access_date", SqlDbType.Date, 0, ArticleSource.ParseDate(r.AccessDate)),
        ("verification_notes", SqlDbType.NVarChar, Max, r.VerificationNotes),
        ("source_json", SqlDbType.NVarChar, Max, item.SourceJson),
        ("content_hash", SqlDbType.Binary, 32, item.ContentHash)
      ];
    }

    private static string BuildMergeSql(List<(string Name, SqlDbType Type, int Size, object? Value)> columns)
    {
      var names = columns.Select(c => c.Name).ToList();
      var updates = names.Where(n => n != "article_code").Select(n => $"{n} = @{n}");

      return $"""
        MERGE dbo.article WITH (HOLDLOCK) AS t
        USING (SELECT @article_code AS article_code) AS s
          ON t.article_code = s.article_code
        WHEN MATCHED THEN UPDATE SET
          {string.Join(",\n  ", updates)},
          embedding       = CASE @embedding_action WHEN 'set' THEN @embedding       WHEN 'clear' THEN NULL ELSE t.embedding       END,
          embedding_model = CASE @embedding_action WHEN 'set' THEN @embedding_model WHEN 'clear' THEN NULL ELSE t.embedding_model END,
          embedded_at     = CASE @embedding_action WHEN 'set' THEN SYSUTCDATETIME() WHEN 'clear' THEN NULL ELSE t.embedded_at     END,
          loaded_at       = SYSUTCDATETIME()
        WHEN NOT MATCHED THEN
          INSERT ({string.Join(", ", names)}, embedding, embedding_model, embedded_at)
          VALUES ({string.Join(", ", names.Select(n => "@" + n))},
                  CASE WHEN @embedding_action = 'set' THEN @embedding END,
                  CASE WHEN @embedding_action = 'set' THEN @embedding_model END,
                  CASE WHEN @embedding_action = 'set' THEN SYSUTCDATETIME() END)
        OUTPUT $action, inserted.article_id;
        """;
    }

    private async Task<SqlConnection> OpenAsync(CancellationToken cancellationToken)
    {
      var connection = new SqlConnection(connectionString);
      await connection.OpenAsync(cancellationToken);
      return connection;
    }
  }
}
