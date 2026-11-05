using Babesiosis.Core.Models.Articles;
using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Experiments
{
  /// <summary>
  /// One tidied dataset (dbo.dataset), loaded by Babesiosis.Console from core/data/tidy/&lt;code&gt;.json.
  /// Its per-subject values are in <see cref="Observation"/>, keyed by <see cref="Variable"/> and <see cref="Subject"/>.
  /// </summary>
  public class Dataset
  {
    public int Id { get; set; }
    /// <summary>Review dataset id, e.g. DS05 or S-CB050.</summary>
    public string Code { get; set; }
    public string Title { get; set; }
    /// <summary>The linked article's review code, e.g. CB126. Kept as text so the link survives an article reload.</summary>
    public string ArticleCode { get; set; }
    public int? ArticleId { get; set; }
    public string Repository { get; set; }
    /// <summary>DOI or accession of the repository record.</summary>
    public string SourceRecord { get; set; }
    public string Licence { get; set; }
    /// <summary>Independent-source group, e.g. SRC-F.</summary>
    public string IndependentSource { get; set; }
    public string Species { get; set; }
    public string Design { get; set; }
    /// <summary>Path of the raw file under core/.</summary>
    public string SourceFile { get; set; }
    public string SourceSha256 { get; set; }
    public int SubjectCount { get; set; }
    /// <summary>JSON array of cleaning notes written by the tidy script.</summary>
    public string Notes { get; set; }
    public DateTime? ExtractedAt { get; set; }
    public DateTime LoadedAt { get; set; }

    public virtual Article Article { get; set; }
    public virtual ICollection<Variable> Variables { get; set; } = new List<Variable>();
    public virtual ICollection<Subject> Subjects { get; set; } = new List<Subject>();
    public virtual ICollection<Experiment> Experiments { get; set; } = new List<Experiment>();
  }
}
