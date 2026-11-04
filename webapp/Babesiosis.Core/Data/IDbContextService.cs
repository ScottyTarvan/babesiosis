using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Data
{
  public interface IDbContextService
  {
    TDbContext CreateDbContext<TDbContext>(bool trackChanges = false) where TDbContext : DbContext;
    TDbContext CreateDbContext<TDbContext>(string cnString, bool trackChanges = false) where TDbContext : DbContext;
    TDbContext CreateDbContext<TDbContext>(SqlConnection connection, bool trackChanges = false) where TDbContext : DbContext;
  }
}
