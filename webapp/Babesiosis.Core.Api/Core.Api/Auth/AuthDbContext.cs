using Babesiosis.Core.Data;
using Babesiosis.Core.Data.Configs.Auth;
using Babesiosis.Core.Models.Auth;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Api.Auth
{
  public class AuthDbContext : DbContextBase
  {
    public AuthDbContext(DbContextOptions<AuthDbContext> options)
        : base(options)
    {
      //nop
    }

    public AuthDbContext(DbContextOptions<AuthDbContext> options, IDbContextQuery query)
      : base(options, query)
    {
      //nop
    }


    public DbSet<PasswordReset> PasswordResets { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
      base.OnConfiguring(optionsBuilder);
    }


    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
      base.OnModelCreating(modelBuilder);

      modelBuilder.ApplyConfiguration(new PasswordResetConfig());
    }
  }
}
