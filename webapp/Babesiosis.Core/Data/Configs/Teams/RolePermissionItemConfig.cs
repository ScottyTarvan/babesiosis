using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class RolePermissionItemConfig : IEntityTypeConfiguration<RolePermissionItem>
  {
    public void Configure(EntityTypeBuilder<RolePermissionItem> builder)
    {
      builder.ToTable("RolePermissionItem", "team");
      builder.HasKey(e => new { e.RoleId, e.PermissionId });
      builder.HasOne(e => e.Role)
        .WithMany(e => e.PermissionItems)
        .HasForeignKey(e => e.RoleId)
        .OnDelete(DeleteBehavior.Cascade);
    }
  }
}
