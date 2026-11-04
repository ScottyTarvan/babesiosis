using System.IO;

namespace Babesiosis.Core.Models.Domain
{
  public class FileModel
  {
    public Stream Stream { get; set; }
    public string ContentType { get; set; }
    public string Name { get; set; }
  }
}
