using System.Data;
using System.Threading.Tasks;

namespace Babesiosis.Core.Data
{
  public interface IDbContextQuery
  {
    Task<int> ExecuteNonQuery(string sql, CommandType commandType, params (string Name, object Value)[] parameters);
    Task<T> ExecuteScalar<T>(string sql, CommandType commandType, params (string Name, object Value)[] parameters);
    Task<IDataReader> ExecuteReader(string sql, CommandType commandType, params (string Name, object Value)[] parameters);
    Task ExecuteBulkCopy(DataTable dataTable, string schema, string tableName);
    Task<DataTable> GetSchemaTable(string sql);
    Task<bool> DoesTableExist(string schema, string tableName);
    Task<bool> DoesViewExist(string viewName);
    Task<bool> DoesPrimaryKeyExist(string schema, string tableName);
    Task<bool> DoesForeignKeyExist(string schema, string tableName, string foreignKeyName);
  }
}
