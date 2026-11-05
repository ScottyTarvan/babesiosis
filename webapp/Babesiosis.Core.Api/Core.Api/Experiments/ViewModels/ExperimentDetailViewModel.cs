using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Experiments.ViewModels
{
  /// <summary>
  /// One experiment in full: header, dataset, variable dictionary, association rows and the
  /// method-specific result payloads. JSON columns travel as strings; the client parses them,
  /// so the wire shape does not depend on which serializer the host uses.
  /// </summary>
  public class ExperimentDetailViewModel
  {
    public string Code { get; set; }
    public string Name { get; set; }
    public string Description { get; set; }
    public string Method { get; set; }
    /// <summary>The run's parameters, JSON.</summary>
    public string Parameters { get; set; }
    public string Script { get; set; }
    public string ScriptVersion { get; set; }
    public DateTime? RunAt { get; set; }
    public int? SubjectCount { get; set; }
    public int? VariableCount { get; set; }
    public int? TestCount { get; set; }
    /// <summary>Significant and not trivial, counted over every association of the run, not only the rows returned.</summary>
    public int FindingCount { get; set; }
    public int SignificantCount { get; set; }
    public string Summary { get; set; }
    public ExperimentDatasetViewModel Dataset { get; set; }
    public List<ExperimentVariableViewModel> Variables { get; set; } = new List<ExperimentVariableViewModel>();
    /// <summary>Best adjusted p first; filtered and capped by the command.</summary>
    public List<ExperimentAssociationViewModel> Associations { get; set; } = new List<ExperimentAssociationViewModel>();
    /// <summary>True when the cap cut the association rows.</summary>
    public bool AssociationsTruncated { get; set; }
    public List<ExperimentResultViewModel> Results { get; set; } = new List<ExperimentResultViewModel>();
  }

  public class ExperimentDatasetViewModel
  {
    public string Code { get; set; }
    public string Title { get; set; }
    public string ArticleCode { get; set; }
    public string ArticleTitle { get; set; }
    /// <summary>Where the linked article opens outside this application; null when unknown.</summary>
    public string ArticleSourceUrl { get; set; }
    public string Repository { get; set; }
    public string SourceRecord { get; set; }
    public string Licence { get; set; }
    public string IndependentSource { get; set; }
    public string Species { get; set; }
    public int SubjectCount { get; set; }
    /// <summary>JSON array of the tidy script's cleaning notes.</summary>
    public string Notes { get; set; }
  }

  public class ExperimentVariableViewModel
  {
    public string Code { get; set; }
    public string Name { get; set; }
    public string Unit { get; set; }
    /// <summary>N, O, C, D or T.</summary>
    public string DataType { get; set; }
    public string Domain { get; set; }
    public bool Derived { get; set; }
    /// <summary>JSON array of parent codes.</summary>
    public string DerivedFrom { get; set; }
    public bool IncludeDefault { get; set; }
    public double? RefLow { get; set; }
    public double? RefHigh { get; set; }
    public string Description { get; set; }
    /// <summary>JSON object of level to count, categorical variables only.</summary>
    public string Levels { get; set; }
  }

  public class ExperimentAssociationViewModel
  {
    public string VariableA { get; set; }
    public string VariableAName { get; set; }
    public string VariableB { get; set; }
    public string VariableBName { get; set; }
    public string Test { get; set; }
    public double? Estimate { get; set; }
    public string EstimateLabel { get; set; }
    public int N { get; set; }
    public double? PValue { get; set; }
    public double? PAdjusted { get; set; }
    public bool Significant { get; set; }
    public bool Trivial { get; set; }
    public string Direction { get; set; }
    /// <summary>JSON detail: statistic, medians, contingency table.</summary>
    public string Detail { get; set; }
  }

  public class ExperimentResultViewModel
  {
    public string Kind { get; set; }
    public string Title { get; set; }
    /// <summary>JSON payload whose shape depends on <see cref="Kind"/>.</summary>
    public string Payload { get; set; }
    public short SortOrder { get; set; }
  }
}
