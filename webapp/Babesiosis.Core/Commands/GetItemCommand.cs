using Babesiosis.Core.Models;
using System;

namespace Babesiosis.Core.Commands
{
  public class GetItemCommand<T>
  {
    public T ItemId { get; set; }
  }
}
