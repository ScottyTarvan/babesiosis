using Babesiosis.Core.Data;
using Babesiosis.Core.Data.Configs.Teams;
using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Teams
{
  public class TeamsDbContext : DbContextBase
  {
    public TeamsDbContext(DbContextOptions<TeamsDbContext> options)
        : base(options)
    {
      //nop
    }

    public TeamsDbContext(DbContextOptions<TeamsDbContext> options, IDbContextQuery query)
      : base(options, query)
    {
      //nop
    }

    public DbSet<UserNotification> UserNotifications { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
      base.OnConfiguring(optionsBuilder);
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
      base.OnModelCreating(modelBuilder);

      modelBuilder.ApplyConfiguration(new UserNotificationConfig());
    }
  }
}
