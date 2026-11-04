using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.ViewModels.Charts
{
  public class DailyMetricsViewModel 
  {
    public Guid InstanceId { get; set; } = Guid.NewGuid();
    public DateTime? Date { get; set; }
    public string DateName { get; set; }
    public int Day { get; set; }
    public string DayName { get; set; }
    public bool IsDifferentMonth { get; set; }
    public int Count { get; set; }
    public decimal Avg { get; set; }
    public decimal Min { get; set; }
    public decimal Max { get; set; }

    public override string ToString()
    {
      return $"{Date}:{Count}";
    }
  }
}
