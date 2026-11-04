using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class RolePermissionConfig : IEntityTypeConfiguration<RolePermission>
  {
    public void Configure(EntityTypeBuilder<RolePermission> builder)
    {
      builder.ToTable("RolePermission", "team");
      builder.HasKey(e => new { e.RoleId, e.PermissionId });
      builder.HasOne(e => e.Role).WithMany(e => e.Permissions).HasForeignKey(e => e.RoleId);
    }
  }
}
