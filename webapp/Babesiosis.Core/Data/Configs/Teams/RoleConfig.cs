using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class RoleConfig : IEntityTypeConfiguration<Role>
  {
    public void Configure(EntityTypeBuilder<Role> builder)
    {
      builder.ToTable("Role", "team");
      builder.HasKey(e => e.Id);
      builder.Property(e => e.RowVersion).IsRowVersion();
    }
  }
}
