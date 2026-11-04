using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Models.Events
{
  public class EventMessage
  {
    public string Subject { get; set; }
    public string EventType { get; set; }
    public object Data { get; set; }
  }
}
