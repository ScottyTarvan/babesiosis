using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Articles
{
  public class ArticleConfig : IEntityTypeConfiguration<Article>
  {
    public void Configure(EntityTypeBuilder<Article> builder)
    {
      builder.ToTable("article", "dbo", t =>
        t.HasCheckConstraint("CK_article_pub_date_precision", "[pub_date_precision] IN ('D', 'M', 'Y')"));
      builder.HasKey(e => e.Id).HasName("PK_article").IsClustered();

      builder.Property(e => e.Id).HasColumnName("article_id").UseIdentityColumn();

      // Keys
      builder.Property(e => e.Code).HasColumnName("article_code").HasMaxLength(10).IsUnicode(false).IsRequired();
      builder.Property(e => e.SourceKey).HasColumnName("source_key").HasMaxLength(50).IsUnicode(false).IsRequired();
      builder.Property(e => e.FileName).HasColumnName("file_name").HasMaxLength(200).IsRequired();

      // Bibliographic
      builder.Property(e => e.Title).HasColumnName("title").HasMaxLength(500).IsRequired();
      builder.Property(e => e.Authors).HasColumnName("authors").HasMaxLength(1000);
      builder.Property(e => e.Journal).HasColumnName("journal").HasMaxLength(300);
      builder.Property(e => e.VolumeIssuePages).HasColumnName("volume_issue_pages").HasMaxLength(150);
      builder.Property(e => e.Doi).HasColumnName("doi").HasMaxLength(100).IsUnicode(false);
      builder.Property(e => e.Pmid).HasColumnName("pmid").HasMaxLength(20).IsUnicode(false);
      builder.Property(e => e.Pmcid).HasColumnName("pmcid").HasMaxLength(20).IsUnicode(false);
      builder.Property(e => e.Language).HasColumnName("language").HasMaxLength(100);
      builder.Property(e => e.Corrections).HasColumnName("corrections").HasMaxLength(400);

      // Dates
      builder.Property(e => e.PubDate).HasColumnName("pub_date").HasColumnType("date");
      // Cast through int: an expression tree has no direct char <-> enum conversion.
      builder.Property(e => e.PubDatePrecision).HasColumnName("pub_date_precision").HasMaxLength(1).IsFixedLength().IsUnicode(false)
        .HasConversion(v => ((char)(int)v).ToString(), v => (DatePrecision)(int)v[0]);
      builder.Property(e => e.PubYear).HasColumnName("pub_year");
      builder.Property(e => e.FirstPubDateText).HasColumnName("first_pub_date_text").HasMaxLength(10).IsUnicode(false);
      builder.Property(e => e.OnlineDateText).HasColumnName("online_date_text").HasMaxLength(200);
      builder.Property(e => e.IssueDateText).HasColumnName("issue_date_text").HasMaxLength(200);
      builder.Property(e => e.DateNote).HasColumnName("date_note").HasMaxLength(800);

      // Study
      builder.Property(e => e.ScopeLabel).HasColumnName("scope_label").HasMaxLength(50);
      builder.Property(e => e.IncludeType).HasColumnName("include_type").HasMaxLength(20).IsUnicode(false);
      builder.Property(e => e.StudyType).HasColumnName("study_type").HasMaxLength(300);
      builder.Property(e => e.OlderFoundational).HasColumnName("older_foundational");
      builder.Property(e => e.Design).HasColumnName("design").HasMaxLength(1000);
      builder.Property(e => e.EvidenceType).HasColumnName("evidence_type").HasMaxLength(150);
      builder.Property(e => e.Host).HasColumnName("host").HasMaxLength(400);
      builder.Property(e => e.Country).HasColumnName("country").HasMaxLength(300);
      builder.Property(e => e.SpeciesSummary).HasColumnName("species_summary").HasMaxLength(200);
      builder.Property(e => e.Species).HasColumnName("species").HasColumnType("json");
      builder.Property(e => e.SampleSize).HasColumnName("sample_size").HasMaxLength(400);
      builder.Property(e => e.InfectedDogCount).HasColumnName("n_infected_dogs");
      builder.Property(e => e.ControlCount).HasColumnName("n_controls");
      builder.Property(e => e.CohortId).HasColumnName("cohort_id").HasMaxLength(10).IsUnicode(false);

      // Category
      builder.Property(e => e.PrimaryCategoryId).HasColumnName("primary_category_id");

      // Narrative
      builder.Property(e => e.OneSentenceFinding).HasColumnName("one_sentence_finding").HasMaxLength(1000);
      builder.Property(e => e.AbstractSummary).HasColumnName("abstract_summary");
      builder.Property(e => e.AuthorsConclusion).HasColumnName("authors_conclusion");
      builder.Property(e => e.ReviewerInterpretation).HasColumnName("reviewer_interpretation");
      builder.Property(e => e.KeyLimitations).HasColumnName("key_limitations");
      builder.Property(e => e.Relevance).HasColumnName("relevance");
      builder.Property(e => e.EvidenceBasis).HasColumnName("evidence_basis");
      builder.Property(e => e.Markdown).HasColumnName("markdown").IsRequired();

      // Sources and data availability
      builder.Property(e => e.AbstractAvailable).HasColumnName("abstract_available");
      builder.Property(e => e.AbstractSource).HasColumnName("abstract_source").HasMaxLength(400);
      builder.Property(e => e.FulltextChecked).HasColumnName("fulltext_checked");
      builder.Property(e => e.FulltextUrl).HasColumnName("fulltext_url").HasMaxLength(400);
      builder.Property(e => e.SupplementChecked).HasColumnName("supplement_checked");
      builder.Property(e => e.RepositoryChecked).HasColumnName("repository_checked");
      builder.Property(e => e.DataAvailabilityStatement).HasColumnName("data_availability_statement").HasMaxLength(600);
      builder.Property(e => e.DatasetStatusCode).HasColumnName("dataset_status_code");
      builder.Property(e => e.DatasetStatus).HasColumnName("dataset_status").HasMaxLength(100);
      builder.Property(e => e.DatasetIds).HasColumnName("dataset_ids").HasColumnType("json");
      builder.Property(e => e.SourceLinks).HasColumnName("source_links").HasColumnType("json");
      builder.Property(e => e.AccessDate).HasColumnName("access_date").HasColumnType("date");
      builder.Property(e => e.VerificationNotes).HasColumnName("verification_notes").HasMaxLength(2000);
      builder.Property(e => e.TextSource).HasColumnName("text_source").HasMaxLength(20).IsUnicode(false);

      // Embedding
      builder.Property(e => e.Embedding).HasColumnName("embedding").HasColumnType("vector(1536)");
      builder.Property(e => e.EmbeddingModel).HasColumnName("embedding_model").HasMaxLength(100).IsUnicode(false);
      builder.Property(e => e.EmbeddedAt).HasColumnName("embedded_at").HasColumnType("datetime2(0)");

      // Audit
      builder.Property(e => e.SourceJson).HasColumnName("source_json").HasColumnType("json").IsRequired();
      builder.Property(e => e.ContentHash).HasColumnName("content_hash").HasColumnType("binary(32)").IsRequired();
      builder.Property(e => e.LoadedAt).HasColumnName("loaded_at").HasColumnType("datetime2(0)")
        .HasDefaultValueSql("sysutcdatetime()", "DF_article_loaded_at");

      builder.HasOne(e => e.PrimaryCategory).WithMany(e => e.PrimaryArticles)
        .HasForeignKey(e => e.PrimaryCategoryId)
        .HasConstraintName("FK_article_category")
        .OnDelete(DeleteBehavior.NoAction);

      builder.HasIndex(e => e.Code).HasDatabaseName("UQ_article_code").IsUnique();
      builder.HasIndex(e => e.SourceKey).HasDatabaseName("UQ_article_source_key").IsUnique();
      builder.HasIndex(e => e.PrimaryCategoryId).HasDatabaseName("IX_article_primary_category");
      builder.HasIndex(e => e.PubYear).HasDatabaseName("IX_article_pub_year");
    }
  }
}
