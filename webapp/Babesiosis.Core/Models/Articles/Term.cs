using System.Collections.Generic;

namespace Babesiosis.Core.Models.Articles
{
  /// <summary>
  /// A UMLS disorder concept found in the articles (dbo.term), loaded by Babesiosis.Console
  /// from core/data/terms with the curated display map core/data/terms/term_display.csv.
  /// </summary>
  public class Term
  {
    public int Id { get; set; }
    /// <summary>UMLS CUI, e.g. C0002871.</summary>
    public string Cui { get; set; }
    /// <summary>UMLS preferred name, e.g. "Anemia".</summary>
    public string Concept { get; set; }
    /// <summary>Semantic type names, "; "-separated.</summary>
    public string SemanticType { get; set; }
    /// <summary>Label that merges several CUIs into one term; null = use <see cref="Concept"/>.</summary>
    public string DisplayName { get; set; }
    /// <summary>True for generic or mislinked concepts the dashboard leaves out.</summary>
    public bool Hidden { get; set; }
    /// <summary>Why the term was hidden, merged or renamed.</summary>
    public string Note { get; set; }

    public virtual ICollection<ArticleTerm> ArticleTerms { get; set; } = new List<ArticleTerm>();
  }
}
