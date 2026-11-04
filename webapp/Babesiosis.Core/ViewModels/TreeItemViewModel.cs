using System;
using System.Collections.Generic;

namespace Babesiosis.Core.ViewModels
{
  public class TreeItemViewModel 
  {
    public Guid InstanceId { get; set; }
    public string Id { get; set; }
    public string ParentId { get; set; }
    public bool IsDirectory { get; set; }
    public bool HasItems { get; set; } = true;
    public string Name { get; set; }
    public string Path { get; set; }
    public long Size { get; set; }
    public bool Selected { get; set; }
    public bool Expanded { get; set; }
    public List<TreeItemViewModel> Children { get; set; } = new List<TreeItemViewModel>();

    public override string ToString()
    {
      return $"Id: {Id}, Name: {Name}, Path: {Path}, Directory: {IsDirectory}";
    }
  }
}
