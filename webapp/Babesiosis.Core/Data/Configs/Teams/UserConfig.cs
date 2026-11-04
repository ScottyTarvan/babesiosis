using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using NPOI.POIFS.FileSystem;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class UserConfig : IEntityTypeConfiguration<User>
  {
    public void Configure(EntityTypeBuilder<User> builder)
    {
      builder.ToTable("User", "team");
      builder.HasKey(e => e.Id).IsClustered();
      builder.Property(e => e.RowVersion).IsRowVersion();
    }
  }
}
