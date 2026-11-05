using System;

namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>One value of one variable for one subject at one time point (dbo.observation, long format).</summary>
  public class Observation
  {
    public long Id { get; set; }
    public int SubjectId { get; set; }
    public int VariableId { get; set; }
    /// <summary>Empty string for single-visit data.</summary>
    public string TimePoint { get; set; }
    public double? ValueNum { get; set; }
    public string ValueText { get; set; }
    public DateOnly? ValueDate { get; set; }

    public virtual Subject Subject { get; set; }
    public virtual Variable Variable { get; set; }
  }
}
