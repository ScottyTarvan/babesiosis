using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Articles
{
  public class CategoryConfig : IEntityTypeConfiguration<Category>
  {
    public void Configure(EntityTypeBuilder<Category> builder)
    {
      builder.ToTable("category", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_category").IsClustered();

      builder.Property(e => e.Id).HasColumnName("category_id").UseIdentityColumn();
      builder.Property(e => e.Code).HasColumnName("category_code").HasMaxLength(3).IsFixedLength().IsUnicode(false).IsRequired();
      builder.Property(e => e.Name).HasColumnName("name").HasMaxLength(100).IsRequired();
      builder.Property(e => e.Label).HasColumnName("label").HasMaxLength(100);
      builder.Property(e => e.SortOrder).HasColumnName("sort_order");

      builder.HasIndex(e => e.Code).HasDatabaseName("UQ_category_code").IsUnique();
      builder.HasIndex(e => e.Name).HasDatabaseName("UQ_category_name").IsUnique();
    }
  }
}
