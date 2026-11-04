using System;

namespace Babesiosis.Core.Models.Domain
{

  public class BlobModel
  {
    public BlobModel(string name = "", string link = "", long? size = null)
    {
      Name = name;
      Link = link;
      SizeKb = size ?? 0;
    }

    public bool IsPrefix { get; set; }
    public string Prefix { get; set; }
    public string Name { get; set; }
    public string Link { get; set; }
    public long SizeKb { get; set; }
    public string ETag { get; set; }

    public override string ToString()
    {
      return $"Name: {Name}, IsPrefix: {IsPrefix}";
    }
  }
}
