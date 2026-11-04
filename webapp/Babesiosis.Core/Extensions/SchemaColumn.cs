using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Extensions
{
  public class SchemaColumn
  {
    public int Ordinal { get; set; }
    public string Name { get; set; }
    public string DataType { get; set; }
    public bool AllowNull { get; set; }
  }
}
