using Babesiosis.Core.Extensions;
using Microsoft.Data.SqlClient;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Storage;
using System;
using System.Data;
using System.Data.Common;
using System.Diagnostics;
using System.Threading.Tasks;
using static Microsoft.EntityFrameworkCore.DbLoggerCategory.Database;

namespace Babesiosis.Core.Data
{
  public class DbContextQuery : IDbContextQuery
  {
    private DbContextBase _dbContext;

    public DbContextQuery(DbContextBase dbContext)
    {
      _dbContext = dbContext;
    }

    public async Task<int> ExecuteNonQuery(string sql, CommandType commandType, params (string Name, object Value)[] parameters)
    {
      using SqlConnection cn = CreateConnection();
      SqlCommand cmd = CreateCommand(cn, commandType, sql);
      foreach (var param in parameters)
      {
        cmd.Parameters.AddWithValue(param.Name, ParamValue(param.Value));
      }
      if (cn.State != ConnectionState.Open)
      {
        await cn.OpenAsync();
      }
      return await cmd.ExecuteNonQueryAsync();
    }

    public async Task<T> ExecuteScalar<T>(string sql, CommandType commandType, params (string Name, object Value)[] parameters)
    {
      using SqlConnection cn = CreateConnection();
      SqlCommand cmd = CreateCommand(cn, commandType, sql);
      foreach (var param in parameters)
      {
        cmd.Parameters.AddWithValue(param.Name, ParamValue(param.Value));
      }
      if (cn.State != ConnectionState.Open)
      {
        await cn.OpenAsync();
      }
      return (T)await cmd.ExecuteScalarAsync();
    }

    public async Task<IDataReader> ExecuteReader(string sql, CommandType commandType = CommandType.Text, params (string Name, object Value)[] parameters)
    {
      SqlConnection cn = CreateConnection();
      SqlCommand cmd = CreateCommand(cn, commandType, sql);
      foreach (var param in parameters)
      {
        cmd.Parameters.AddWithValue(param.Name, ParamValue(param.Value));
      }
      if (cn.State != ConnectionState.Open)
      {
        await cn.OpenAsync();
      }
      return await cmd.ExecuteReaderAsync(CommandBehavior.CloseConnection);
    }

    private object ParamValue(object value)
    {
      return value == null ? DBNull.Value : value;
    }

    public async Task ExecuteBulkCopy(DataTable dataTable, string schema, string tableName)
    { 
      using SqlConnection cn = this.CreateConnection();
      using SqlBulkCopy bcp = new SqlBulkCopy(cn);

      foreach (DataColumn column in dataTable.Columns)
      {
        bcp.ColumnMappings.Add(column.ColumnName, column.ColumnName);
      }
      bcp.DestinationTableName = $"[{schema}].[{tableName}]";
      if (cn.State != ConnectionState.Open)
      {
        await cn.OpenAsync();
      }
      await bcp.WriteToServerAsync(dataTable);
    }

    public async Task<DataTable> GetSchemaTable(string sql)
    {
      SqlConnection cn = CreateConnection();
      SqlCommand cmd = CreateCommand(cn, CommandType.Text, sql);
      if (cn.State != ConnectionState.Open)
      {
        await cn.OpenAsync();
      }
      SqlDataReader reader = await cmd.ExecuteReaderAsync(CommandBehavior.KeyInfo);
      return reader.GetSchemaTable();
    }

    public async Task<bool> DoesTableExist(string schema, string tableName)
    {
      string sql = $"select count(tab.name) from sys.tables tab " +
        "inner join sys.schemas sch " +
        "on sch.schema_id = tab.schema_id " +
        $"where sch.name = '{schema}' " +
        $"and tab.name='{tableName}'";

      return await this.ExecuteScalar<int>(sql, CommandType.Text) > 0;
    }

    public async Task<bool> DoesViewExist(string viewName)
    {
      string sql = $"select count(name) from sys.views where name='{viewName}'";
      return await this.ExecuteScalar<int>(sql, CommandType.Text) > 0;
    }

    public async Task<bool> DoesPrimaryKeyExist(string schema, string tableName)
    {
      string sql = "select count(ind.name) " +
        "from sys.indexes ind " +
        "inner join sys.tables tab " +
        "on tab.object_id = ind.object_id " +
        "inner join sys.schemas sch " +
        "on sch.schema_id = tab.schema_id " +
        "where ind.is_primary_key = 1 " +
        $"and sch.name = '{schema}' " +
        $"and tab.name = '{tableName}'";

      return await this.ExecuteScalar<int>(sql, CommandType.Text) > 0;
    }

    public async Task<bool> DoesForeignKeyExist(string schema, string tableName, string foreignKeyName)
    {
      string sql = "select count(fk.name) " +
        "from sys.foreign_keys as fk " +
        "inner join sys.tables as tab " +
        "on fk.parent_object_id = tab.object_id " +
        "inner join sys.schemas sch " +
        "on sch.schema_id = tab.schema_id " +
        $"where sch.name = '{schema}' " +
        $"and tab.name = '{tableName}' " +
        $"and fk.name = '{foreignKeyName}'";

      return await this.ExecuteScalar<int>(sql, CommandType.Text) > 0;
    }

    private SqlConnection CreateConnection()
    {
      var cn = this._dbContext.Database.GetDbConnection();
      return cn as SqlConnection;
    }

    private SqlCommand CreateCommand(SqlConnection cn, CommandType commandType, string sql)
    {
      return new SqlCommand()
      {
        Connection = cn,
        CommandText = sql,
        CommandType = commandType
      };
    }
  }
}
