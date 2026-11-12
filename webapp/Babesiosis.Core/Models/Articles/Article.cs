using Microsoft.Data.SqlTypes;
using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Articles
{
  /// <summary>One reviewed article (dbo.article), loaded by Babesiosis.Console from the review files.</summary>
  public class Article
  {
    public int Id { get; set; }

    // Keys
    /// <summary>Review code, e.g. CB001.</summary>
    public string Code { get; set; }
    /// <summary>Source identifier, e.g. PMID:28074976.</summary>
    public string SourceKey { get; set; }
    public string FileName { get; set; }

    // Bibliographic
    public string Title { get; set; }
    /// <summary>Display string, e.g. "Abdoli A, Olfatifar M, ...".</summary>
    public string Authors { get; set; }
    public string Journal { get; set; }
    public string VolumeIssuePages { get; set; }
    public string Doi { get; set; }
    public string Pmid { get; set; }
    public string Pmcid { get; set; }
    public string Language { get; set; }
    public string Corrections { get; set; }

    // Dates
    public DateOnly? PubDate { get; set; }
    public DatePrecision? PubDatePrecision { get; set; }
    public short? PubYear { get; set; }
    public string FirstPubDateText { get; set; }
    public string OnlineDateText { get; set; }
    public string IssueDateText { get; set; }
    public string DateNote { get; set; }

    // Study
    public string ScopeLabel { get; set; }
    public string IncludeType { get; set; }
    public string StudyType { get; set; }
    public bool? OlderFoundational { get; set; }
    public string Design { get; set; }
    public string EvidenceType { get; set; }
    public string Host { get; set; }
    public string Country { get; set; }
    /// <summary>
    /// Country tidied from <see cref="Country"/> (computed, persisted column): the text before the
    /// first "(", ";", "," or "/", with a few spellings merged. Null when no country is stated.
    /// </summary>
    public string CountryNormalised { get; set; }
    public string SpeciesSummary { get; set; }
    /// <summary>JSON array of {name, status, method}.</summary>
    public string Species { get; set; }
    public string SampleSize { get; set; }
    public int? InfectedDogCount { get; set; }
    public int? ControlCount { get; set; }
    public string CohortId { get; set; }

    // Category. Null when the source has no category code or holds free text instead of one.
    public int? PrimaryCategoryId { get; set; }
    /// <summary>"high" or "low" from the NLP category step; null when NLP found no category (computed from source_json).</summary>
    public string CategoryConfidence { get; set; }
    /// <summary>"nlp", or "agent (NLP found no category)" for a fallback label (computed from source_json).</summary>
    public string CategorySource { get; set; }

    // Narrative, from the article .md file
    public string OneSentenceFinding { get; set; }
    public string AbstractSummary { get; set; }
    public string AuthorsConclusion { get; set; }
    public string ReviewerInterpretation { get; set; }
    public string KeyLimitations { get; set; }
    public string Relevance { get; set; }
    public string EvidenceBasis { get; set; }
    /// <summary>The whole article file, verbatim.</summary>
    public string Markdown { get; set; }

    // Sources and data availability
    public bool? AbstractAvailable { get; set; }
    public string AbstractSource { get; set; }
    public bool? FulltextChecked { get; set; }
    public string FulltextUrl { get; set; }
    public bool? SupplementChecked { get; set; }
    public bool? RepositoryChecked { get; set; }
    public string DataAvailabilityStatement { get; set; }
    public byte? DatasetStatusCode { get; set; }
    public string DatasetStatus { get; set; }
    /// <summary>JSON array of dataset ids, e.g. ["S-CB005"].</summary>
    public string DatasetIds { get; set; }
    /// <summary>JSON.</summary>
    public string SourceLinks { get; set; }
    public DateOnly? AccessDate { get; set; }
    public string VerificationNotes { get; set; }
    /// <summary>Where the article's terms come from: abstract, jats_xml or pdf. Null before the term load.</summary>
    public string TextSource { get; set; }

    // Embedding
    // SqlVector is a struct, so it has to be Nullable for rows that have not been embedded yet.
    public SqlVector<float>? Embedding { get; set; }
    public string EmbeddingModel { get; set; }
    public DateTime? EmbeddedAt { get; set; }

    // Audit
    /// <summary>The articles.jsonl record, verbatim (JSON).</summary>
    public string SourceJson { get; set; }
    /// <summary>SHA-256 of the embedded text; the loader re-embeds when it changes.</summary>
    public byte[] ContentHash { get; set; }
    /// <summary>UTC. Defaults to SYSUTCDATETIME() on insert.</summary>
    public DateTime LoadedAt { get; set; }

    public virtual Category PrimaryCategory { get; set; }
    public virtual ICollection<ArticleCategory> ArticleCategories { get; set; } = new List<ArticleCategory>();
    public virtual ICollection<ArticleTerm> ArticleTerms { get; set; } = new List<ArticleTerm>();
  }
}
