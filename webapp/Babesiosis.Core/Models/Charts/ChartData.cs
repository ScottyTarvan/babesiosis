using System.Collections.Generic;

namespace Babesiosis.Core.Models.Charts
{
  public class ChartData
  {
    public List<string> Labels { get; set; } = new List<string>();
    public List<Series> Series { get; set; } = new List<Series>();
  }
}
