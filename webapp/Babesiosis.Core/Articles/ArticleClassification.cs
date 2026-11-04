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
  /// The study-type and Babesia-species labels shared by the Review dashboard's
  /// Evidence profile and the Articles grid, so both screens agree on every article.
  ///
  /// Study type: IncludeType "review" is Reviews and "case_report" is Case reports;
  /// otherwise the EvidenceType text decides, in this order: mechanistic or
  /// experimental, prognostic, associational, else Descriptive.
  ///
  /// Species: the one species the SpeciesSummary text names among canis, gibsoni,
  /// rossi and vogeli. "B. canis vogeli" and "B. canis rossi" count as vogeli and
  /// rossi; none or several species give Mixed / unspecified.
  ///
  /// The rules are written as a queryable projection, not C# methods, so they
  /// translate to SQL (CASE and LIKE) and the grid can filter and sort on the
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
    public const string MixedOrUnspecified = "Mixed / unspecified";

    /// <summary>Every study-type label, in display order.</summary>
    public static readonly string[] StudyTypes =
    {
      Descriptive, Associational, Mechanistic, Prognostic, CaseReports, Reviews
    };

    /// <summary>Every species label, in display order.</summary>
    public static readonly string[] SpeciesGroups =
    {
      Canis, Gibsoni, Rossi, Vogeli, MixedOrUnspecified
    };

    /// <summary>Each article with its two labels, computed in the database.</summary>
    public static IQueryable<ClassifiedArticle> Classified(this IQueryable<Article> articles) =>
      articles.Select(a => new ClassifiedArticle
      {
        Article = a,
        StudyType =
          a.IncludeType == "review" ? Reviews
          : a.IncludeType == "case_report" ? CaseReports
          : (a.EvidenceType ?? "").ToLower().Contains("mechanistic")
            || (a.EvidenceType ?? "").ToLower().Contains("experimental") ? Mechanistic
          : (a.EvidenceType ?? "").ToLower().Contains("prognostic") ? Prognostic
          : (a.EvidenceType ?? "").ToLower().Contains("associational") ? Associational
          : Descriptive,
        Species =
          (a.SpeciesSummary ?? "").ToLower().Contains("canis vogeli")
            && !(a.SpeciesSummary ?? "").ToLower().Contains("gibsoni")
            && !(a.SpeciesSummary ?? "").ToLower().Contains("rossi") ? Vogeli
          : (a.SpeciesSummary ?? "").ToLower().Contains("canis rossi")
            && !(a.SpeciesSummary ?? "").ToLower().Contains("gibsoni")
            && !(a.SpeciesSummary ?? "").ToLower().Contains("vogeli") ? Rossi
          : ((a.SpeciesSummary ?? "").ToLower().Contains("canis") ? 1 : 0)
            + ((a.SpeciesSummary ?? "").ToLower().Contains("gibsoni") ? 1 : 0)
            + ((a.SpeciesSummary ?? "").ToLower().Contains("rossi") ? 1 : 0)
            + ((a.SpeciesSummary ?? "").ToLower().Contains("vogeli") ? 1 : 0) == 1
            ? ((a.SpeciesSummary ?? "").ToLower().Contains("canis") ? Canis
              : (a.SpeciesSummary ?? "").ToLower().Contains("gibsoni") ? Gibsoni
              : (a.SpeciesSummary ?? "").ToLower().Contains("rossi") ? Rossi
              : Vogeli)
          : MixedOrUnspecified
      });
  }
}
