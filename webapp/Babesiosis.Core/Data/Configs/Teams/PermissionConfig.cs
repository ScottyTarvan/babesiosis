using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class PermissionConfig : IEntityTypeConfiguration<Permission>
  {
    public void Configure(EntityTypeBuilder<Permission> builder)
    {
      builder.ToTable("Permission", "team");
      builder.HasKey(e => e.Id);
      builder.Property(e => e.RowVersion).IsRowVersion();
    }
  }
}
