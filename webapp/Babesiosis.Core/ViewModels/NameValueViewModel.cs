using Babesiosis.Core.Extensions;
using System;

namespace Babesiosis.Core.ViewModels
{
  public class NameValueViewModel<TValue> : ViewModel
  {
    public NameValueViewModel(string name, TValue value, bool selected = false)
    {
      Name = name;
      Value = value;
      Selected = selected;
    }

    public NameValueViewModel(string name, TValue value)
    {
      Name = name;
      Value = value;
    }

    public NameValueViewModel(Enum @enum, bool selected = false)
    {
      Name = @enum.GetDescription();
      Value = (TValue)Convert.ChangeType(@enum, typeof(object));
      Selected = selected;
    }

    public NameValueViewModel(Enum @enum)
    {
      Name = @enum.GetDescription();
      Value = (TValue)Convert.ChangeType(@enum, typeof(object));
    }

    public NameValueViewModel() { }

    public string Name { get; set; }
    public string Description { get; set; }
    public TValue Value { get; set; }
  }
}
