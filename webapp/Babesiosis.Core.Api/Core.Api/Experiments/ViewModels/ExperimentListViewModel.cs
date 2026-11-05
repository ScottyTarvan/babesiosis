using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Experiments.ViewModels
{
  /// <summary>Every experiment run, newest first, for the Experiments screen's left-hand panel.</summary>
  public class ExperimentListViewModel
  {
    public List<ExperimentListItemViewModel> Items { get; set; } = new List<ExperimentListItemViewModel>();
    /// <summary>Distinct datasets among the runs, for the panel's grouping.</summary>
    public int DatasetCount { get; set; }
  }

  /// <summary>One run in the panel: enough to pick it, nothing of its results.</summary>
  public class ExperimentListItemViewModel
  {
    public string Code { get; set; }
    public string Name { get; set; }
    /// <summary>pairwise_association, clustering, ...</summary>
    public string Method { get; set; }
    public string DatasetCode { get; set; }
    public string DatasetTitle { get; set; }
    /// <summary>The dataset's linked article code, e.g. CB126. Null when the dataset has none.</summary>
    public string ArticleCode { get; set; }
    public string ArticleTitle { get; set; }
    public DateTime? RunAt { get; set; }
    public int? SubjectCount { get; set; }
    public int? VariableCount { get; set; }
    public int? TestCount { get; set; }
    /// <summary>Associations significant after adjustment and not trivial.</summary>
    public int FindingCount { get; set; }
    public string Summary { get; set; }
  }
}
