using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Teams
{
  public class UserNotificationConfig : IEntityTypeConfiguration<UserNotification>
  {
    public void Configure(EntityTypeBuilder<UserNotification> builder)
    {
      builder.ToTable("UserNotification", "team");
      builder.HasKey(e => e.Id).IsClustered();
    }
  }
}
