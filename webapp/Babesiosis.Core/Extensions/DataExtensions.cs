using System;
using System.Collections;
using System.Collections.Generic;
using System.Data;

namespace Babesiosis.Core.Extensions
{
  public static class DataExtensions
  {
    public static bool IsDBNull(this IDataReader reader, string columnName)
    {
      return reader.IsDBNull(reader.GetOrdinal(columnName));
    }

    public static T Field<T>(this IDataReader reader, string columnName)
    {
      return reader.IsDBNull(columnName) ? default(T) : (T)reader[columnName];
    }
    
    public static IEnumerable<SchemaColumn> GetSchema(this IDataReader reader)
    {
      var schema = reader.GetSchemaTable();
      
      foreach (DataRow row in schema.Rows)
      {
        yield return new SchemaColumn
        {
          Ordinal = (int)row["ColumnOrdinal"],
          Name = (string)row["ColumnName"],
          DataType = (string)row["DataTypeName"],
          AllowNull = (bool)row["AllowDBNull"]
        };
      }
    }

    public static bool HasColumn(this IDataRecord reader, string columnName)
    {
      for (int i = 0; i < reader.FieldCount; i++)
      {
        if (reader.GetName(i).Equals(columnName, StringComparison.OrdinalIgnoreCase))
        {
          return true;
        }
      }
      return false;
    }
  }
}
