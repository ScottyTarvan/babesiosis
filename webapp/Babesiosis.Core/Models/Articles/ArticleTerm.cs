namespace Babesiosis.Core.Models.Articles
{
  /// <summary>
  /// A term with at least one affirmed mention in an article (dbo.article_term).
  /// </summary>
  public class ArticleTerm
  {
    public int ArticleId { get; set; }
    public int TermId { get; set; }
    public int Mentions { get; set; }
    public int MentionsAffirmed { get; set; }
    public int MentionsNegated { get; set; }
    /// <summary>
    /// Mentioned in the title, results, case or conclusion (or, for abstract-only articles, the abstract);
    /// false = mentioned only.
    /// </summary>
    public bool Studied { get; set; }
    /// <summary>JSON object of mentions per section, e.g. {"abstract": 4, "title": 1}.</summary>
    public string Sections { get; set; }
    /// <summary>JSON object of surface forms, e.g. {"anaemia": 3}.</summary>
    public string Forms { get; set; }
    /// <summary>Best UMLS link score (threshold 0.85).</summary>
    public decimal? BestScore { get; set; }

    public virtual Article Article { get; set; }
    public virtual Term Term { get; set; }
  }
}
