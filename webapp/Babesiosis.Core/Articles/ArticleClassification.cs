using Babesiosis.Core.Models.Articles;
using System.Linq;

namespace Babesiosis.Core.Articles
{
  /// <summary>An article with the study-type and species labels <see cref="ArticleClassification"/> derives for it.</summary>
  public class ClassifiedArticle
  {
    public Article Article { get; set; }
    /// <summary>One of <see cref="ArticleClassification.StudyTypes"/>.</summary>
    public string StudyType { get; set; }
    /// <summary>One of <see cref="ArticleClassification.SpeciesGroups"/>.</summary>
    public string Species { get; set; }
  }

  /// <summary>
  /// The study-type and Babesia-species labels shared by the overview, the topic pages and
  /// the Articles grid, so every screen agrees on every article.
  ///
  /// Study type: IncludeType "review" is Reviews and "case_report" is Case reports;
  /// otherwise the EvidenceType text decides, in this order: mechanistic or
  /// experimental, prognostic, associational, else Descriptive.
  ///
  /// Species, from the lower-cased SpeciesSummary text:
  /// <list type="bullet">
  /// <item>Text that starts "mixed/unspecified", or is empty, names no species.</item>
  /// <item>Each of B. canis, B. gibsoni, B. rossi and B. vogeli counts as named when its
  /// name appears; "other" counts when vulpes, microti, conradae, negevi, Rangelia
  /// vitalii, Theileria annae or "sp. coco" appears.</item>
  /// <item>B. canis needs "b. canis" or "babesia canis", never a bare "canis" (so "E. canis"
  /// co-infection text does not count), after "b. canis vogeli", "b. canis (vogeli)" and
  /// "b. canis rossi" are removed: those name B. vogeli and B. rossi. "b. c. vogeli" is vogeli.</item>
  /// <item>One named species gives that species (Other named species for "other"); two or
  /// more, or text that starts "multiple", give Multiple species. None gives Not identified in text
  /// read, except for a review (IncludeType "review"), which covers several species and so is
  /// Multiple species. "Not identified in text read" means the abstract or full text that was
  /// appraised names no species (often abstract-only, or a smear-only diagnosis).</item>
  /// </list>
  ///
  /// The rules are written as a queryable projection, not C# methods, so they
  /// translate to SQL (CASE, LIKE and REPLACE) and the grid can filter and sort on the
  /// labels server-side. Both fields come from the extraction agents, not human review.
  /// </summary>
  public static class ArticleClassification
  {
    public const string Descriptive = "Descriptive";
    public const string Associational = "Associational";
    public const string Mechanistic = "Mechanistic / experimental";
    public const string Prognostic = "Prognostic";
    public const string CaseReports = "Case reports";
    public const string Reviews = "Reviews";

    public const string Canis = "B. canis";
    public const string Gibsoni = "B. gibsoni";
    public const string Rossi = "B. rossi";
    public const string Vogeli = "B. vogeli";
    public const string MultipleSpecies = "Multiple species";
    public const string OtherNamedSpecies = "Other named species";
    public const string NotIdentified = "Not identified in text read";

    /// <summary>Every study-type label, in display order.</summary>
    public static readonly string[] StudyTypes =
    {
      Descriptive, Associational, Mechanistic, Prognostic, CaseReports, Reviews
    };

    /// <summary>Every species label, in display order.</summary>
    public static readonly string[] SpeciesGroups =
    {
      Canis, Gibsoni, Rossi, Vogeli, MultipleSpecies, OtherNamedSpecies, NotIdentified
    };

    /// <summary>The species text with its named-species flags, the intermediate step of <see cref="Classified"/>.</summary>
    private sealed class SpeciesFlags
    {
      public Article Article { get; set; }
      public string Text { get; set; }
      public bool Unspecified { get; set; }
      public bool Multiple { get; set; }
      public int Canis { get; set; }
      public int Gibsoni { get; set; }
      public int Rossi { get; set; }
      public int Vogeli { get; set; }
      public int Other { get; set; }
    }

    /// <summary>Each article with its two labels, computed in the database.</summary>
    public static IQueryable<ClassifiedArticle> Classified(this IQueryable<Article> articles) =>
      articles
        .Select(a => new { Article = a, Text = (a.SpeciesSummary ?? "").ToLower() })
        .Select(x => new
        {
          x.Article,
          x.Text,
          // The text with the B. canis subspecies names taken out, so "b. canis" left in it is B. canis itself.
          CanisText = x.Text.Replace("b. canis vogeli", "").Replace("b. canis (vogeli)", "")
            .Replace("babesia canis vogeli", "").Replace("b. canis rossi", "").Replace("babesia canis rossi", "")
        })
        .Select(x => new SpeciesFlags
        {
          Article = x.Article,
          Text = x.Text,
          Unspecified = x.Text == "" || x.Text.StartsWith("mixed/unspecified"),
          Multiple = x.Text.StartsWith("multiple"),
          Canis = x.CanisText.Contains("b. canis") || x.CanisText.Contains("babesia canis") ? 1 : 0,
          Gibsoni = x.Text.Contains("gibsoni") ? 1 : 0,
          Rossi = x.Text.Contains("rossi") ? 1 : 0,
          Vogeli = x.Text.Contains("vogeli") ? 1 : 0,
          Other = x.Text.Contains("vulpes") || x.Text.Contains("microti") || x.Text.Contains("conradae")
            || x.Text.Contains("negevi") || x.Text.Contains("vitalii") || x.Text.Contains("annae")
            || x.Text.Contains("sp. coco") ? 1 : 0
        })
        .Select(f => new ClassifiedArticle
        {
          Article = f.Article,
          StudyType =
            f.Article.IncludeType == "review" ? Reviews
            : f.Article.IncludeType == "case_report" ? CaseReports
            : (f.Article.EvidenceType ?? "").ToLower().Contains("mechanistic")
              || (f.Article.EvidenceType ?? "").ToLower().Contains("experimental") ? Mechanistic
            : (f.Article.EvidenceType ?? "").ToLower().Contains("prognostic") ? Prognostic
            : (f.Article.EvidenceType ?? "").ToLower().Contains("associational") ? Associational
            : Descriptive,
          Species =
            f.Unspecified ? (f.Article.IncludeType == "review" ? MultipleSpecies : NotIdentified)
            : f.Multiple || f.Canis + f.Gibsoni + f.Rossi + f.Vogeli + f.Other > 1 ? MultipleSpecies
            : f.Canis == 1 ? Canis
            : f.Gibsoni == 1 ? Gibsoni
            : f.Rossi == 1 ? Rossi
            : f.Vogeli == 1 ? Vogeli
            : f.Other == 1 ? OtherNamedSpecies
            : f.Article.IncludeType == "review" ? MultipleSpecies
            : NotIdentified
        });
  }
}
