using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Charts
{
  public class Series
  {
    public string Name { get; set; }
    public List<SeriesData> Data { get; set; } = new List<SeriesData>();

    public Series(string name = null)
    {
      Name = name;
    }

    public void AddData((string Key, object Value) data)
    {
      this.Data.Add(new SeriesData(data));
    }
    
    public void AddPercentage(string key, double value, double total)
    {
      var percentage = (total == 0) ? 0 : Math.Min(100, (value / total) * 100);
      this.Data.Add(new SeriesData((key, percentage)));
    } 
   
  }
}
