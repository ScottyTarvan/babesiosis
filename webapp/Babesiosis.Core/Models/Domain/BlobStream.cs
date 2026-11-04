using System;
using System.IO;
using Babesiosis.Core.Extensions;

namespace Babesiosis.Core.Models.Domain
{
  public class BlobStream
  {
    public BlobStream(Stream blob, string name)
    {
      Blob = blob;
      Name = name ?? Guid.NewGuid().ToD();
    }

    public string Name { get; set; }
    public Stream Blob { get; set; }
  }
}
