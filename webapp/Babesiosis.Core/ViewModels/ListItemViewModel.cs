using Babesiosis.Core.Extensions;
using System;

namespace Babesiosis.Core.ViewModels
{
  public class ListItemViewModel<TId> : ViewModel
  {
    public ListItemViewModel()
    {
      //nop
    }

    public ListItemViewModel(TId id, string name)
    {
      Id = id;
      Name = name;
    }

    public ListItemViewModel(TId id, string name, string tag)
    {
      Id = id;
      Name = name;
      Tag = tag;
    }

    public ListItemViewModel(Enum @enum)
    {
      Id = (TId)Convert.ChangeType(@enum, typeof(object));
      Name = @enum.GetDescription();
    }

    public TId Id { get; set; }
    public string Name { get; set; }
    public string Tag { get; set; }
  }
}
