using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using NPOI.POIFS.FileSystem;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class UserRoleConfig : IEntityTypeConfiguration<UserRole>
  {
    public void Configure(EntityTypeBuilder<UserRole> builder)
    {
      builder.ToTable("UserRole", "team");
      builder.HasKey(e => new { e.UserId, e.RoleId });
    }
  }
}
