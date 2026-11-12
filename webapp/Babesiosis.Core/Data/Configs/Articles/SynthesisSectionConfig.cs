using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Articles
{
  public class SynthesisSectionConfig : IEntityTypeConfiguration<SynthesisSection>
  {
    public void Configure(EntityTypeBuilder<SynthesisSection> builder)
    {
      builder.ToTable("synthesis_section", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_synthesis_section").IsClustered();

      builder.Property(e => e.Id).HasColumnName("synthesis_section_id").UseIdentityColumn();
      builder.Property(e => e.DocumentCode).HasColumnName("document_code").HasMaxLength(10).IsUnicode(false).IsRequired();
      builder.Property(e => e.SectionOrder).HasColumnName("section_order");
      builder.Property(e => e.SectionKey).HasColumnName("section_key").HasMaxLength(60).IsUnicode(false).IsRequired();
      builder.Property(e => e.Heading).HasColumnName("heading").HasMaxLength(400).IsRequired();
      builder.Property(e => e.Body).HasColumnName("body").IsRequired();
      builder.Property(e => e.SourceFile).HasColumnName("source_file").HasMaxLength(200).IsRequired();
      builder.Property(e => e.FileModifiedAt).HasColumnName("file_modified_at").HasColumnType("datetime2(0)");
      builder.Property(e => e.LoadedAt).HasColumnName("loaded_at").HasColumnType("datetime2(0)")
        .HasDefaultValueSql("sysutcdatetime()", "DF_synthesis_section_loaded_at");

      builder.HasIndex(e => new { e.DocumentCode, e.SectionOrder }).HasDatabaseName("UQ_synthesis_section_order").IsUnique();
      builder.HasIndex(e => new { e.DocumentCode, e.SectionKey }).HasDatabaseName("UQ_synthesis_section_key").IsUnique();
    }
  }
}
