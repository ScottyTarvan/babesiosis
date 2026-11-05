using System.Data;
using System.Text.Json;
using Babesiosis.Console.Source;
using Microsoft.Data;
using Microsoft.Data.SqlClient;
using Microsoft.Data.SqlTypes;

namespace Babesiosis.Console.Data
{
  /// <summary>What dbo.article and dbo.article_section currently hold for one article.</summary>
  internal sealed record ExistingText(int ArticleId, byte[]? TextHash, int PassageCount, int UnembeddedCount);

  /// <summary>Writes an article's passages to dbo.article_section and its text columns on dbo.article.</summary>
  internal sealed class SectionRepository(string connectionString, int dimensions)
  {
    public async Task<bool> SchemaExistsAsync(CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT CASE WHEN OBJECT_ID(N'dbo.article_section', N'U') IS NOT NULL
                     AND COL_LENGTH(N'dbo.article', N'text_hash') IS NOT NULL
                    THEN 1 ELSE 0 END;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      return (int)(await command.ExecuteScalarAsync(cancellationToken))! == 1;
    }

    /// <summary>Every article in the database, by code, with its stored text hash and passage counts.</summary>
    public async Task<Dictionary<string, ExistingText>> GetExistingAsync(CancellationToken cancellationToken)
    {
      const string sql = """
        SELECT a.article_code, a.article_id, a.text_hash,
               COUNT(s.section_id) AS passages,
               SUM(CASE WHEN s.section_id IS NOT NULL AND s.embedding IS NULL THEN 1 ELSE 0 END) AS unembedded
        FROM dbo.article AS a
        LEFT JOIN dbo.article_section AS s ON s.article_id = a.article_id
        GROUP BY a.article_code, a.article_id, a.text_hash;
        """;

      await using var connection = await OpenAsync(cancellationToken);
      await using var command = new SqlCommand(sql, connection);
      await using var reader = await command.ExecuteReaderAsync(cancellationToken);

      var existing = new Dictionary<string, ExistingText>(StringComparer.OrdinalIgnoreCase);
      while (await reader.ReadAsync(cancellationToken))
      {
        existing[reader.GetString(0)] = new ExistingText(
          reader.GetInt32(1),
          reader.IsDBNull(2) ? null : (byte[])reader[2],
          reader.GetInt32(3),
          reader.GetInt32(4));
      }
      return existing;
    }

    /// <summary>
    /// Replaces the article's passages and updates its text columns in one transaction.
    /// <paramref name="vectors"/> has one entry per passage, in order, or is null to store the
    /// passages without embeddings (they are embedded on the next full run).
    /// </summary>
    public async Task ReplaceAsync(
      int articleId, ArticleText text, float[][]? vectors, string embeddingModel, CancellationToken cancellationToken)
    {
      if (vectors is not null && vectors.Length != text.Passages.Count)
        throw new ArgumentException("One vector per passage is required.", nameof(vectors));

      await using var connection = await OpenAsync(cancellationToken);
      await using var transaction = (SqlTransaction)await connection.BeginTransactionAsync(cancellationToken);

      await using (var delete = new SqlCommand("DELETE FROM dbo.article_section WHERE article_id = @article_id;", connection, transaction))
      {
        delete.Parameters.Add(new SqlParameter("@article_id", SqlDbType.Int) { Value = articleId });
        await delete.ExecuteNonQueryAsync(cancellationToken);
      }

      const string insertSql = """
        INSERT INTO dbo.article_section
          (article_id, section_order, section_kind, heading, chunk_index, chunk_count, body, word_count,
           embedding, embedding_model, embedded_at)
        VALUES
          (@article_id, @section_order, @section_kind, @heading, @chunk_index, @chunk_count, @body, @word_count,
           @embedding,
           CASE WHEN @has_embedding = 1 THEN @embedding_model END,
           CASE WHEN @has_embedding = 1 THEN SYSUTCDATETIME() END);
        """;

      await using (var insert = new SqlCommand(insertSql, connection, transaction))
      {
        var pArticle = insert.Parameters.Add(new SqlParameter("@article_id", SqlDbType.Int) { Value = articleId });
        var pOrder = insert.Parameters.Add(new SqlParameter("@section_order", SqlDbType.SmallInt));
        var pKind = insert.Parameters.Add(new SqlParameter("@section_kind", SqlDbType.VarChar, 20));
        var pHeading = insert.Parameters.Add(new SqlParameter("@heading", SqlDbType.NVarChar, 300));
        var pChunk = insert.Parameters.Add(new SqlParameter("@chunk_index", SqlDbType.SmallInt));
        var pChunks = insert.Parameters.Add(new SqlParameter("@chunk_count", SqlDbType.SmallInt));
        var pBody = insert.Parameters.Add(new SqlParameter("@body", SqlDbType.NVarChar, -1));
        var pWords = insert.Parameters.Add(new SqlParameter("@word_count", SqlDbType.Int));
        var pEmbedding = insert.Parameters.Add(new SqlParameter("@embedding", SqlDbTypeExtensions.Vector));
        var pHasEmbedding = insert.Parameters.Add(new SqlParameter("@has_embedding", SqlDbType.Bit));
        insert.Parameters.Add(new SqlParameter("@embedding_model", SqlDbType.VarChar, 100) { Value = embeddingModel });

        for (var i = 0; i < text.Passages.Count; i++)
        {
          var passage = text.Passages[i];
          var vector = vectors?[i];

          pOrder.Value = (short)passage.Order;
          pKind.Value = passage.Kind;
          pHeading.Value = (object?)passage.Heading ?? DBNull.Value;
          pChunk.Value = (short)passage.ChunkIndex;
          pChunks.Value = (short)passage.ChunkCount;
          pBody.Value = passage.Body;
          pWords.Value = passage.WordCount;
          pEmbedding.Value = vector is null ? SqlVector<float>.CreateNull(dimensions) : new SqlVector<float>(vector);
          pHasEmbedding.Value = vector is not null;

          await insert.ExecuteNonQueryAsync(cancellationToken);
        }
      }

      const string updateSql = """
        UPDATE dbo.article SET
          has_full_text   = @has_full_text,
          text_source     = @text_source,
          text_quality    = @text_quality,
          text_flags      = @text_flags,
          text_language   = @text_language,
          text_translated = @text_translated,
          text_word_count = @text_word_count,
          text_file       = @text_file,
          text_hash       = @text_hash,
          text_loaded_at  = SYSUTCDATETIME()
        WHERE article_id = @article_id;
        """;

      await using (var update = new SqlCommand(updateSql, connection, transaction))
      {
        update.Parameters.Add(new SqlParameter("@article_id", SqlDbType.Int) { Value = articleId });
        update.Parameters.Add(new SqlParameter("@has_full_text", SqlDbType.Bit) { Value = text.HasFullText });
        update.Parameters.Add(new SqlParameter("@text_source", SqlDbType.VarChar, 20) { Value = (object?)text.SourceFormat ?? DBNull.Value });
        update.Parameters.Add(new SqlParameter("@text_quality", SqlDbType.VarChar, 20) { Value = (object?)text.Quality ?? DBNull.Value });
        update.Parameters.Add(new SqlParameter("@text_flags", SqlDbType.NVarChar, -1) { Value = JsonSerializer.Serialize(text.QualityFlags) });
        update.Parameters.Add(new SqlParameter("@text_language", SqlDbType.VarChar, 30) { Value = (object?)text.Language ?? DBNull.Value });
        update.Parameters.Add(new SqlParameter("@text_translated", SqlDbType.Bit) { Value = text.Translated });
        update.Parameters.Add(new SqlParameter("@text_word_count", SqlDbType.Int) { Value = text.WordCount });
        update.Parameters.Add(new SqlParameter("@text_file", SqlDbType.NVarChar, 200) { Value = text.File });
        update.Parameters.Add(new SqlParameter("@text_hash", SqlDbType.Binary, 32) { Value = text.ContentHash });
        await update.ExecuteNonQueryAsync(cancellationToken);
      }

      await transaction.CommitAsync(cancellationToken);
    }

    private async Task<SqlConnection> OpenAsync(CancellationToken cancellationToken)
    {
      var connection = new SqlConnection(connectionString);
      await connection.OpenAsync(cancellationToken);
      return connection;
    }
  }
}
