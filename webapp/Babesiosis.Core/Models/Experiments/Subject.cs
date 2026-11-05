namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>One animal, or one sample where animals are not identified (dbo.subject).</summary>
  public class Subject
  {
    public int Id { get; set; }
    public int DatasetId { get; set; }
    /// <summary>The dataset's own identifier, e.g. BET001.</summary>
    public string Code { get; set; }
    /// <summary>Study group as the dataset defines it.</summary>
    public string GroupLabel { get; set; }
    /// <summary>Survival or severity class where the dataset has one.</summary>
    public string OutcomeLabel { get; set; }

    public virtual Dataset Dataset { get; set; }
  }
}
