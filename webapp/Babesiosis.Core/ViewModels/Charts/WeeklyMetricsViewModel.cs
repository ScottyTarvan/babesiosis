using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.ViewModels.Charts
{
  public class WeeklyMetricsViewModel
  {
    public List<DailyMetricsViewModel> Days { get; set; } = new List<DailyMetricsViewModel>(); 
  }
}
