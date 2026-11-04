using System.Collections.Generic;

namespace Babesiosis.Core.Models.Charts
{
  public class SeriesData
  {
    public IDictionary<string, object> Values { get; set; }

    public SeriesData(params (string Key, object Value)[] values)
    {
      Values = new Dictionary<string, object>();
      foreach (var (Key, Value) in values)
      {
        Values.Add(Key, Value);
      }
    }

    public void AddValue((string Key, object Value) value)
    {
      if (Values == null)
      {
        Values = new Dictionary<string, object>();
      }
      Values.Add(value.Key, value.Value);
    }

    public SeriesData AddValues(IEnumerable<(string Key, object Value)> values)
    {
      if (Values == null)
      {
        Values = new Dictionary<string, object>();
      }
      foreach (var (Key, Value) in values)
      {
        Values.Add(Key, Value);
      }
      return this;
    }

  }
}
