using Babesiosis.Core.Data.Configs.Teams;
using Babesiosis.Core.Models.Teams;
using Microsoft.EntityFrameworkCore;
using System;
using System.Data;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;

namespace Babesiosis.Core.Data
{
  public class DbContextBase : DbContext
  {
    public DbContextBase(DbContextOptions options) : base(options)
    {
      this.DbQuery = new DbContextQuery(this);
      ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;
    }

    public DbContextBase(DbContextOptions options, IDbContextQuery query) : base(options)
    {
      this.DbQuery = query;
      ChangeTracker.QueryTrackingBehavior = QueryTrackingBehavior.NoTracking;
    }

    public IDbContextQuery DbQuery { get; set; }

    public DbSet<User> Users { get; set; }
    public DbSet<Role> Roles { get; set; }
    public DbSet<UserRole> UserRoles { get; set; }
    public DbSet<Permission> Permissions { get; set; }
    public DbSet<RolePermission> RolePermissions { get; set; }
    public DbSet<RolePermissionItem> RolePermissionItems { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
    {
      base.OnConfiguring(optionsBuilder);
      if (Debugger.IsAttached)
      {
        optionsBuilder.LogTo(Console.WriteLine);
        optionsBuilder.EnableDetailedErrors();
        optionsBuilder.EnableSensitiveDataLogging();
      }
    }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
      modelBuilder.ApplyConfiguration(new UserConfig());
      modelBuilder.ApplyConfiguration(new RoleConfig());
      modelBuilder.ApplyConfiguration(new UserRoleConfig());
      modelBuilder.ApplyConfiguration(new PermissionConfig());
      modelBuilder.ApplyConfiguration(new RolePermissionConfig());
      modelBuilder.ApplyConfiguration(new RolePermissionItemConfig());
    }

    public void LogChanges()
    {
      var trackedEntities = ChangeTracker.Entries()
          .Where(e => e.State != EntityState.Unchanged) 
          .ToList();

      foreach (var entry in trackedEntities)
      {
        Debug.WriteLine($"Entity: {entry.Entity.GetType().Name}, State: {entry.State}");

        if (entry.State == EntityState.Added || entry.State != EntityState.Modified)
        {
          foreach (var property in entry.Properties)
          {
            if (property.IsModified)
            {
              Debug.WriteLine($"Property: {property.Metadata.Name}");
              Debug.WriteLine($"Original Value: {property.OriginalValue}");
              Debug.WriteLine($"Current Value: {property.CurrentValue}");
            }
          }
        }
      }
    }

    public async Task<int> ExecuteNonQuery(string sql, 
      CommandType commandType, 
      params (string Name, object Value)[] parameters)
    {
      return await this.DbQuery.ExecuteNonQuery(sql, commandType, parameters);
    }

    public async Task<IDataReader> ExecuteReader(string sql, 
      CommandType commandType = CommandType.Text, 
      params (string Name, object Value)[] parameters)
    {
      return await this.DbQuery.ExecuteReader(sql, commandType, parameters);
    } 

    public async Task<T> ExecuteScalar<T>(string sql, CommandType commandType, params (string Name, object Value)[] parameters)
    {
      return await this.DbQuery.ExecuteScalar<T>(sql, commandType, parameters);
    }

    public async Task ExecuteBulkCopy(DataTable dataTable, string schema, string tableName)
    {
      await this.DbQuery.ExecuteBulkCopy(dataTable, schema, tableName);
    }

    public async Task<DataTable> GetSchemaTable(string sql)
    {
      return await this.DbQuery.GetSchemaTable(sql);
    }

    public async Task<bool> DoesTableExist(string schema, string tableName)
    {
      return await this.DbQuery.DoesTableExist(schema, tableName);
    }

    public async Task<bool> DoesViewExist(string viewName)
    {
      return await this.DbQuery.DoesViewExist(viewName);
    }

    public async Task<bool> DoesPrimaryKeyExist(string schema, string tableName)
    {
      return await this.DbQuery.DoesPrimaryKeyExist(schema, tableName);
    }

    public async Task<bool> DoesForeignKeyExist(string schema, string tableName, string foreignKeyName)
    {
      return await this.DbQuery.DoesForeignKeyExist(schema, tableName, foreignKeyName);
    }
  }
}
