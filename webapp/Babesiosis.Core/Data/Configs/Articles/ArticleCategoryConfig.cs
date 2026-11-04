using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using System;

namespace Babesiosis.Core.Data.Configs.Articles
{
  public class ArticleCategoryConfig : IEntityTypeConfiguration<ArticleCategory>
  {
    public void Configure(EntityTypeBuilder<ArticleCategory> builder)
    {
      builder.ToTable("article_category", "dbo", t =>
        t.HasCheckConstraint("CK_article_category_tag_type", "[tag_type] IN ('secondary', 'comparator')"));
      builder.HasKey(e => new { e.ArticleId, e.CategoryId, e.TagType }).HasName("PK_article_category").IsClustered();

      builder.Property(e => e.ArticleId).HasColumnName("article_id");
      builder.Property(e => e.CategoryId).HasColumnName("category_id");
      // The check constraint wants the lower-case name, not the enum's Pascal-case ToString().
      builder.Property(e => e.TagType).HasColumnName("tag_type").HasMaxLength(10).IsUnicode(false)
        .HasConversion(v => v.ToString().ToLowerInvariant(), v => Enum.Parse<ArticleTagType>(v, true));

      builder.HasOne(e => e.Article).WithMany(e => e.ArticleCategories)
        .HasForeignKey(e => e.ArticleId)
        .HasConstraintName("FK_article_category_article")
        .OnDelete(DeleteBehavior.Cascade);
      builder.HasOne(e => e.Category).WithMany(e => e.ArticleCategories)
        .HasForeignKey(e => e.CategoryId)
        .HasConstraintName("FK_article_category_category")
        .OnDelete(DeleteBehavior.NoAction);

      builder.HasIndex(e => new { e.CategoryId, e.TagType }).HasDatabaseName("IX_article_category_category");
    }
  }
}
