using System.Collections.Concurrent;
using System.ComponentModel;
using Microsoft.Extensions.AI;

namespace Babesiosis.Agents.Clinical
{
  /// <summary>
  /// The functions the agent can call over the clinical manual (<see cref="ClinicalManual"/>):
  /// the list of pages, one page by section, and a keyword search over every page. One instance
  /// serves one question and records the pages the tools returned.
  /// </summary>
  internal sealed class ClinicalManualTools
  {
    public const int MaxResults = 20;

    /// <summary>Characters of one search result; a longer block is cut and the model reads the section.</summary>
    public const int MaxHitChars = 1_200;

    /// <summary>Words that are on every page, or that carry no meaning, and so cannot rank a block.</summary>
    private static readonly HashSet<string> StopWords = new(StringComparer.OrdinalIgnoreCase)
    {
      "the", "and", "for", "with", "what", "which", "how", "does", "are", "was", "were", "when", "from", "that",
      "this", "can", "should", "about", "into", "used", "use", "dog", "dogs", "canine", "babesiosis", "babesia"
    };

    private readonly ClinicalManual _manual;
    private readonly ConcurrentDictionary<string, byte> _seen = new(StringComparer.OrdinalIgnoreCase);

    public ClinicalManualTools(ClinicalManual manual)
    {
      _manual = manual;
    }

    /// <summary>How many distinct pages the tools have returned so far.</summary>
    public int SeenCount => _seen.Count;

    public IList<AITool> AsTools() =>
    [
      AIFunctionFactory.Create(ListClinicalPages, "list_clinical_pages"),
      AIFunctionFactory.Create(GetClinicalPage, "get_clinical_page"),
      AIFunctionFactory.Create(SearchClinicalManual, "search_clinical_manual")
    ];

    [Description(
      "The pages of the clinical manual: one per clinical syndrome of canine babesiosis (SY01 to " +
      "SY16) and one for antibabesial drugs (TX00). Returns each page's ID, group, title, " +
      "definition and the names of its treatments. Call it to find which page covers a syndrome " +
      "or a treatment, then read the page with get_clinical_page.")]
    private IReadOnlyList<ClinicalPageSummary> ListClinicalPages()
    {
      return _manual.Pages
        .Select(p => new ClinicalPageSummary(p.Id, p.Group, p.Title, p.Updated, p.Definition, p.Treatments))
        .ToList();
    }

    [Description(
      "One page of the clinical manual, as Markdown, by section. Sections: overview (definition, " +
      "key points, description, mechanism, differences between Babesia species), diagnosis " +
      "(criteria with thresholds, clinical signs, tests, differential diagnoses, grading), " +
      "approach (the steps in order), treatments (each treatment with its class, status, " +
      "evidence level, evidence summary, doses, cautions and monitoring), prognosis, gaps (what " +
      "is not known, and the literature search behind the page) and references (the full list). " +
      "Ask only for the sections the question needs. The text cites the page's references as " +
      "[R1]; the result ends with one line for each reference it cites, with the review's " +
      "article code where the paper is in the review.")]
    private ClinicalPageText GetClinicalPage(
      [Description("The page ID, e.g. \"SY05\" or \"TX00\".")]
      string pageId,
      [Description("The sections to return: overview, diagnosis, approach, treatments, prognosis, gaps, references, or all (everything but the full reference list). Default: overview.")]
      string[]? sections = null)
    {
      var page = _manual.Find(pageId);
      if (page is null)
      {
        return new ClinicalPageText(pageId?.Trim() ?? "", "", "", [], "",
          $"The manual has no page \"{pageId}\". Its pages are: {PageList()}.");
      }

      var wanted = NormaliseSections(sections, out var unknown);
      _seen.TryAdd(page.Id, 0);

      // The fixed notice of the Clinical screen (/clinical/CL-00-shell.md).
      var note = "Compiled by AI agents from the published literature. Not peer reviewed. Check every dose against the product label before use.";
      if (unknown.Count > 0)
        note = $"Unknown sections ignored: {string.Join(", ", unknown)}. Sections are: {string.Join(", ", ClinicalManual.Sections)}. {note}";

      return new ClinicalPageText(page.Id, page.Title, page.Updated, wanted, page.Render(wanted), note);
    }

    [Description(
      "Keyword search over every page of the clinical manual. Finds the criteria, signs, tests, " +
      "differentials, steps, treatments, doses and prognostic indicators whose text holds the " +
      "words of the query, with the page and section each one is in. Use it when the question " +
      "names a drug, a test or a finding rather than a syndrome (\"imidocarb\", \"lactate\", " +
      "\"plasma transfusion\"), or to find a topic across pages. It matches words, not meaning: " +
      "use a few distinctive words, and British spelling (anaemia, oedema, haemolysis). A long " +
      "result is cut short; read the rest with get_clinical_page.")]
    private ClinicalSearchResult SearchClinicalManual(
      [Description("A few distinctive words, e.g. \"diminazene dose\" or \"hypoglycaemia\".")]
      string query,
      [Description("Optional page IDs to search within, e.g. [\"TX00\"]. Empty = all pages.")]
      string[]? pageIds = null,
      [Description("Optional sections to search within: overview, diagnosis, approach, treatments, prognosis, gaps, references. Empty = all but references.")]
      string[]? sections = null,
      [Description("How many results to return, 1 to 20. Default 8.")]
      int top = 8)
    {
      var terms = Terms(query);
      if (terms.Count == 0)
        return new ClinicalSearchResult([], "query is required: give one or more words to look for.");

      var pages = pageIds is { Length: > 0 }
        ? pageIds.Select(_manual.Find).Where(p => p is not null).Select(p => p!).Distinct().ToList()
        : _manual.Pages.ToList();
      if (pages.Count == 0)
        return new ClinicalSearchResult([], $"None of those pages exist. The manual's pages are: {PageList()}.");

      var within = sections is { Length: > 0 }
        ? NormaliseSections(sections, out _)
        : ClinicalManual.Sections.Where(s => s != "references").ToList();

      var hits = new List<(int Matched, int InBlock, ClinicalPage Page, ClinicalBlock Block, List<string> Terms)>();
      foreach (var page in pages)
      {
        foreach (var block in page.Blocks.Where(b => within.Contains(b.Section)))
        {
          var own = $"{block.Group} {block.Label} {block.Text}";
          var inBlock = terms.Where(t => own.Contains(t, StringComparison.OrdinalIgnoreCase)).ToList();
          if (inBlock.Count == 0)
            continue;

          // The page's title gives the block its context: "treatment" of "kidney injury".
          var matched = terms.Where(t => inBlock.Contains(t) || page.Title.Contains(t, StringComparison.OrdinalIgnoreCase)).ToList();
          hits.Add((matched.Count, inBlock.Count, page, block, matched));
        }
      }

      var best = hits
        .OrderByDescending(h => h.Matched)
        .ThenByDescending(h => h.InBlock)
        .Take(Math.Clamp(top, 1, MaxResults))
        .Select(h =>
        {
          _seen.TryAdd(h.Page.Id, 0);
          var text = h.Block.Text.Trim();
          var cut = text.Length > MaxHitChars;
          return new ClinicalSearchHit(
            h.Page.Id, h.Page.Title, h.Block.Section, h.Block.Label,
            cut ? text[..MaxHitChars] + " …" : text, cut, h.Terms);
        })
        .ToList();

      var note = best.Count == 0
        ? $"No block of the manual holds any of: {string.Join(", ", terms)}. Try other words or British spelling, or pick a page from list_clinical_pages."
        : "Reference markers such as [R3] belong to each result's own page; get_clinical_page lists what they are.";
      return new ClinicalSearchResult(best, note);
    }

    private string PageList() => string.Join(", ", _manual.Pages.Select(p => $"{p.Id} ({p.Title})"));

    /// <summary>The query's distinct words, lower case, without stop words; a plural is searched as its singular.</summary>
    private static List<string> Terms(string? query)
    {
      var words = (query ?? "")
        .Split([' ', '\t', '\r', '\n', ',', ';', ':', '.', '(', ')', '[', ']', '"', '\'', '?', '!', '/'], StringSplitOptions.RemoveEmptyEntries)
        .Select(w => w.ToLowerInvariant())
        .Where(w => w.Length >= 3)
        .Distinct()
        .ToList();

      var kept = words.Where(w => !StopWords.Contains(w)).ToList();
      if (kept.Count == 0)
        kept = words;

      return kept
        .Select(w => w.Length > 4 && w.EndsWith('s') && !w.EndsWith("ss") && !w.EndsWith("is") && !w.EndsWith("us") ? w[..^1] : w)
        .Distinct()
        .ToList();
    }

    private static List<string> NormaliseSections(string[]? sections, out List<string> unknown)
    {
      unknown = [];
      var wanted = new List<string>();

      foreach (var raw in sections ?? [])
      {
        var section = (raw ?? "").Trim().ToLowerInvariant() switch
        {
          "treatment" or "doses" or "dose" or "therapy" => "treatments",
          "diagnostics" or "diagnostic" or "tests" or "signs" => "diagnosis",
          "definition" or "description" or "summary" or "key_points" => "overview",
          "evidence_gaps" or "evidence gaps" => "gaps",
          "reference" => "references",
          var other => other
        };

        if (section == "all")
          wanted.AddRange(ClinicalManual.Sections.Where(s => s != "references"));
        else if (ClinicalManual.Sections.Contains(section))
          wanted.Add(section);
        else if (section.Length > 0)
          unknown.Add(raw!.Trim());
      }

      if (wanted.Count == 0)
        wanted.Add("overview");
      return wanted.Distinct().ToList();
    }
  }

  /// <summary>One row of list_clinical_pages.</summary>
  public sealed record ClinicalPageSummary(
    string Id, string Group, string Title, string Updated, string Definition, IReadOnlyList<string> Treatments);

  /// <summary>The sections of one page, from get_clinical_page.</summary>
  /// <param name="Note">How the page was made, or why there is no text.</param>
  public sealed record ClinicalPageText(
    string Id, string Title, string Updated, IReadOnlyList<string> Sections, string Text, string Note);

  /// <summary>One block of a page that holds words of the query.</summary>
  /// <param name="Item">What the block is: the treatment, test, criterion or heading.</param>
  /// <param name="Truncated">True when <paramref name="Text"/> was cut short.</param>
  public sealed record ClinicalSearchHit(
    string PageId, string PageTitle, string Section, string Item, string Text, bool Truncated, IReadOnlyList<string> MatchedTerms);

  public sealed record ClinicalSearchResult(IReadOnlyList<ClinicalSearchHit> Hits, string Note);
}
