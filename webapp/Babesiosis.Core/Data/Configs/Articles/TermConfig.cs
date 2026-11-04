using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Articles
{
  public class TermConfig : IEntityTypeConfiguration<Term>
  {
    public void Configure(EntityTypeBuilder<Term> builder)
    {
      builder.ToTable("term", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_term").IsClustered();

      builder.Property(e => e.Id).HasColumnName("term_id").UseIdentityColumn();
      builder.Property(e => e.Cui).HasColumnName("cui").HasMaxLength(10).IsUnicode(false).IsRequired();
      builder.Property(e => e.Concept).HasColumnName("concept").HasMaxLength(200).IsRequired();
      builder.Property(e => e.SemanticType).HasColumnName("semantic_type").HasMaxLength(100);
      builder.Property(e => e.DisplayName).HasColumnName("display_name").HasMaxLength(200);
      builder.Property(e => e.Hidden).HasColumnName("hidden").HasDefaultValue(false, "DF_term_hidden");
      builder.Property(e => e.Note).HasColumnName("note").HasMaxLength(400);

      builder.HasIndex(e => e.Cui).HasDatabaseName("UQ_term_cui").IsUnique();
    }
  }
}
