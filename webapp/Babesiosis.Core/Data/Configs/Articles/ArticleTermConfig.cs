using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Articles
{
  public class ArticleTermConfig : IEntityTypeConfiguration<ArticleTerm>
  {
    public void Configure(EntityTypeBuilder<ArticleTerm> builder)
    {
      builder.ToTable("article_term", "dbo");
      builder.HasKey(e => new { e.ArticleId, e.TermId }).HasName("PK_article_term").IsClustered();

      builder.Property(e => e.ArticleId).HasColumnName("article_id");
      builder.Property(e => e.TermId).HasColumnName("term_id");
      builder.Property(e => e.Mentions).HasColumnName("mentions");
      builder.Property(e => e.MentionsAffirmed).HasColumnName("mentions_affirmed");
      builder.Property(e => e.MentionsNegated).HasColumnName("mentions_negated");
      builder.Property(e => e.Studied).HasColumnName("studied");
      builder.Property(e => e.Sections).HasColumnName("sections").HasColumnType("json");
      builder.Property(e => e.Forms).HasColumnName("forms").HasColumnType("json");
      builder.Property(e => e.BestScore).HasColumnName("best_score").HasPrecision(4, 3);

      builder.HasOne(e => e.Article).WithMany(e => e.ArticleTerms)
        .HasForeignKey(e => e.ArticleId)
        .HasConstraintName("FK_article_term_article")
        .OnDelete(DeleteBehavior.Cascade);
      builder.HasOne(e => e.Term).WithMany(e => e.ArticleTerms)
        .HasForeignKey(e => e.TermId)
        .HasConstraintName("FK_article_term_term")
        .OnDelete(DeleteBehavior.NoAction);

      builder.HasIndex(e => e.TermId).HasDatabaseName("IX_article_term_term");
    }
  }
}
