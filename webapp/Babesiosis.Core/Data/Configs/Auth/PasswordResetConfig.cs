using Babesiosis.Core.Models.Auth;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using NPOI.POIFS.FileSystem;

namespace Babesiosis.Core.Data.Configs.Auth
{
  public class PasswordResetConfig : IEntityTypeConfiguration<PasswordReset>
  {
    public void Configure(EntityTypeBuilder<PasswordReset> builder)
    {
      builder.ToTable("PasswordReset", "team");
      builder.HasKey(e => e.Id).IsClustered();
      builder.HasOne(e => e.User).WithMany().HasForeignKey(e => e.UserId);
    }
  }
}
