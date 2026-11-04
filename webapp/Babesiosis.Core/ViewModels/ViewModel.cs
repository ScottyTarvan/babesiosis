using Babesiosis.Core.Models.Domain;
using System;

namespace Babesiosis.Core.ViewModels
{
  public class ViewModel
  {
    public Guid InstanceId { get; set; } = Guid.NewGuid();
    public string RowVersion { get; set; }
    public EditState EditState { get; set; } = EditState.Unchanged;
    public bool Selected { get; set; }
  }
}
