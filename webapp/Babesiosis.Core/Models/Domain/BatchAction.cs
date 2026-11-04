using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Models.Domain
{
  /// <summary>
  /// The values used for loading stored procs when they insert data
  /// </summary>
  public enum BatchAction
  {
    None = 0,
    Insert = 1,
    Update = 2,
    Delete = 3,
    Split = 4
  }
}
