using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.ViewModels
{
  public class FileStreamViewModel
  {
    public Stream Stream { get; set; }
    public string ContentType { get; set; }
    public string Name { get; set; }
  }
}
