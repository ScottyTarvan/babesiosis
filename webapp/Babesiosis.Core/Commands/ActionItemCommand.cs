using Babesiosis.Core.Models.Domain;
using System;

namespace Babesiosis.Core.Commands
{
  public class ActionItemCommand 
  {
    public Guid ItemId { get; set; }
    public string RowVersion { get; set; }
  }
}
