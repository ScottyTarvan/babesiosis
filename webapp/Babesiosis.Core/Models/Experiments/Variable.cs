namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>One measured or recoded column of a dataset (dbo.variable): the variable dictionary.</summary>
  public class Variable
  {
    public int Id { get; set; }
    public int DatasetId { get; set; }
    /// <summary>Stable code within the dataset, e.g. haematocrit, breed_group.</summary>
    public string Code { get; set; }
    public string Name { get; set; }
    /// <summary>The header as it appears in the source file.</summary>
    public string SourceName { get; set; }
    /// <summary>The same measurement across datasets; null until a second dataset is mapped.</summary>
    public string CanonicalCode { get; set; }
    public string Unit { get; set; }
    /// <summary>N numeric, O ordinal, C categorical, D date, T free text.</summary>
    public string DataType { get; set; }
    /// <summary>signalment, clinical, haematology, biochemistry, pathogen, time, derived.</summary>
    public string Domain { get; set; }
    /// <summary>True for a grade or class the authors computed from a measured variable.</summary>
    public bool Derived { get; set; }
    /// <summary>JSON array of codes this variable is an arithmetic function of.</summary>
    public string DerivedFrom { get; set; }
    /// <summary>True when the variable is in the default test set of the experiment scripts.</summary>
    public bool IncludeDefault { get; set; }
    public double? RefLow { get; set; }
    public double? RefHigh { get; set; }
    public string Description { get; set; }
    /// <summary>Categorical variables: JSON object of level to subject count.</summary>
    public string Levels { get; set; }
    public short SortOrder { get; set; }

    public virtual Dataset Dataset { get; set; }
  }
}
