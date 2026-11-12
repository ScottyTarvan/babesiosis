using System.Reflection;
using System.Text;
using System.Text.Json.Nodes;
using System.Text.RegularExpressions;

namespace Babesiosis.Agents.Clinical
{
  /// <summary>
  /// The clinical manual for the agent's tools: one page per clinical syndrome (SY01, ...) and
  /// the antibabesial treatment page (TX00).
  ///
  /// The pages are the JSON files of the web app's Clinical screen
  /// (<c>Babesiosis.Web/public/assets/clinical/</c>, format in <c>/clinical/content-format.md</c>),
  /// embedded in this assembly, so the agent and the screen show the same content. Each page is
  /// turned into short text blocks once, on first use; the tools return and search those blocks.
  /// </summary>
  public sealed partial class ClinicalManual
  {
    public const string ResourcePrefix = "Babesiosis.Agents.Clinical.Pages.";

    /// <summary>The sections of a page, in reading order, as the tools name them.</summary>
    public static readonly IReadOnlyList<string> Sections =
      ["overview", "diagnosis", "approach", "treatments", "prognosis", "gaps", "references"];

    private readonly Lazy<IReadOnlyList<ClinicalPage>> _pages;

    public ClinicalManual() : this(typeof(ClinicalManual).Assembly)
    {
    }

    /// <param name="assembly">The assembly that holds the page files as embedded resources.</param>
    public ClinicalManual(Assembly assembly)
    {
      _pages = new Lazy<IReadOnlyList<ClinicalPage>>(() => Load(assembly));
    }

    /// <summary>Every page, in the order of the Clinical screen's rail.</summary>
    public IReadOnlyList<ClinicalPage> Pages => _pages.Value;

    public ClinicalPage? Find(string? id) =>
      string.IsNullOrWhiteSpace(id)
        ? null
        : Pages.FirstOrDefault(p => string.Equals(p.Id, id.Trim(), StringComparison.OrdinalIgnoreCase));

    /// <summary>The pages whose ID the text mentions (SY05, TX00), in order of first mention.</summary>
    public IReadOnlyList<ClinicalPage> Mentioned(string text)
    {
      var pages = new List<ClinicalPage>();
      foreach (Match match in PageId().Matches(text ?? ""))
      {
        var page = Find(match.Value);
        if (page is not null && !pages.Contains(page))
          pages.Add(page);
      }
      return pages;
    }

    private static IReadOnlyList<ClinicalPage> Load(Assembly assembly)
    {
      var files = new Dictionary<string, JsonObject>(StringComparer.OrdinalIgnoreCase);
      foreach (var name in assembly.GetManifestResourceNames().Where(n => n.StartsWith(ResourcePrefix, StringComparison.Ordinal)))
      {
        using var stream = assembly.GetManifestResourceStream(name)!;
        if (JsonNode.Parse(stream) is JsonObject root)
          files[Path.GetFileNameWithoutExtension(name[ResourcePrefix.Length..])] = root;
      }

      // index.json gives the rail: the groups and the order of the pages.
      var pages = new List<ClinicalPage>();
      if (files.Remove("index", out var index))
      {
        foreach (var group in Items(index, "groups"))
        {
          foreach (var entry in Items(group, "pages"))
          {
            var id = Text(entry, "id");
            if (files.Remove(id, out var root))
              pages.Add(ClinicalPage.Create(id, Text(group, "group"), root));
          }
        }
      }

      // A page that the index does not list is still part of the manual.
      foreach (var (id, root) in files.OrderBy(f => f.Key, StringComparer.OrdinalIgnoreCase))
        pages.Add(ClinicalPage.Create(id, "Other", root));

      return pages;
    }

    internal static string Text(JsonNode? node, string name) => node?[name] switch
    {
      null => "",
      JsonValue value => value.ToString().Trim(),
      var other => other.ToJsonString()
    };

    internal static IEnumerable<JsonNode> Items(JsonNode? node, string name) =>
      node?[name] is JsonArray array ? array.Where(item => item is not null).Select(item => item!) : [];

    [GeneratedRegex(@"\b(?:SY|TX)\d{2}\b")]
    private static partial Regex PageId();
  }

  /// <summary>One text block of a page: a criterion, a test, a treatment, a paragraph.</summary>
  /// <param name="Section">One of <see cref="ClinicalManual.Sections"/>.</param>
  /// <param name="Group">The sub-heading inside the section, e.g. "Diagnostic criteria".</param>
  /// <param name="Label">What the block is about, e.g. the treatment's name.</param>
  /// <param name="Text">The block as plain text, with citation markers such as [R3].</param>
  public sealed record ClinicalBlock(string Section, string Group, string Label, string Text);

  /// <summary>One page of the manual, as text blocks.</summary>
  public sealed partial class ClinicalPage
  {
    private readonly Dictionary<string, string> _references;

    private ClinicalPage(
      string id, string group, string title, string updated, string definition,
      IReadOnlyList<string> treatments, IReadOnlyList<ClinicalBlock> blocks, Dictionary<string, string> references)
    {
      Id = id;
      Group = group;
      Title = title;
      Updated = updated;
      Definition = definition;
      Treatments = treatments;
      Blocks = blocks;
      _references = references;
    }

    /// <summary>SY01 to SY16, or TX00.</summary>
    public string Id { get; }

    /// <summary>The group on the screen's rail: Blood, Organs, ...</summary>
    public string Group { get; }

    public string Title { get; }

    /// <summary>The date the page was written, <c>YYYY-MM-DD</c>.</summary>
    public string Updated { get; }

    public string Definition { get; }

    /// <summary>The names of the page's treatments, in the page's order.</summary>
    public IReadOnlyList<string> Treatments { get; }

    public IReadOnlyList<ClinicalBlock> Blocks { get; }

    /// <summary>
    /// The sections asked for as Markdown, followed by a short line for each reference they
    /// cite, so a claim can be traced without a second call.
    /// </summary>
    public string Render(IReadOnlyCollection<string> sections)
    {
      var text = new StringBuilder();
      text.Append("# ").Append(Id).Append(": ").Append(Title).Append('\n');

      foreach (var section in ClinicalManual.Sections.Where(sections.Contains))
      {
        var blocks = Blocks.Where(b => b.Section == section).ToList();
        if (blocks.Count == 0)
          continue;

        text.Append("\n## ").Append(SectionTitles[section]).Append('\n');
        if (section == "treatments")
          text.Append(TreatmentLegend).Append('\n');

        string? group = null;
        foreach (var block in blocks)
        {
          if (block.Group != group)
          {
            group = block.Group;
            if (group.Length > 0)
              text.Append("\n### ").Append(group).Append('\n');
          }
          text.Append(block.Text).Append('\n');
        }
      }

      if (!sections.Contains("references"))
      {
        var cited = ReferenceMarker().Matches(text.ToString())
          .Select(m => m.Groups[1].Value)
          .Distinct()
          .OrderBy(key => int.Parse(key[1..]))
          .Where(_references.ContainsKey)
          .ToList();

        if (cited.Count > 0)
        {
          text.Append("\n## References cited above\n");
          foreach (var key in cited)
            text.Append(_references[key]).Append('\n');
        }
      }

      return text.ToString().TrimEnd();
    }

    internal static ClinicalPage Create(string id, string group, JsonObject root)
    {
      var blocks = new List<ClinicalBlock>();

      // ---- overview ----
      var definition = T(root, "definition");
      if (definition.Length > 0)
        blocks.Add(new("overview", "", "Definition", $"Definition: {definition}"));
      if (T(root, "definition_note") is { Length: > 0 } definitionNote)
        blocks.Add(new("overview", "", "Note on the definition", $"Note on the definition: {definitionNote}"));
      foreach (var point in ClinicalManual.Items(root, "key_points"))
        blocks.Add(new("overview", "Key points", "Key point", $"- {point}"));
      foreach (var part in ClinicalManual.Items(root, "description"))
        blocks.Add(new("overview", "Description", T(part, "heading"), $"**{T(part, "heading")}.** {T(part, "text")}"));
      foreach (var note in ClinicalManual.Items(root, "species_notes"))
        blocks.Add(new("overview", "Differences between Babesia species", T(note, "species"), $"- {T(note, "species")}: {T(note, "note")}"));
      foreach (var related in ClinicalManual.Items(root, "related"))
        blocks.Add(new("overview", "Related pages", T(related, "id"), $"- {T(related, "id")}: {T(related, "why")}"));

      // ---- diagnosis ----
      var diagnosis = root["diagnosis"];
      foreach (var item in ClinicalManual.Items(diagnosis, "criteria"))
      {
        blocks.Add(new("diagnosis", "Diagnostic criteria", T(item, "criterion"),
          WithRefs($"- {T(item, "criterion")}: {T(item, "threshold")}. Basis of the threshold: {T(item, "basis")}.{Sentence(T(item, "note"))}", item)));
      }
      foreach (var item in ClinicalManual.Items(diagnosis, "clinical_signs"))
        blocks.Add(new("diagnosis", "Clinical signs", T(item, "sign"), WithRefs($"- {T(item, "sign")}.{Sentence(T(item, "note"))}", item)));
      foreach (var item in ClinicalManual.Items(diagnosis, "tests"))
      {
        blocks.Add(new("diagnosis", "Diagnostic tests (basic practice first)", T(item, "test"),
          WithRefs($"- {T(item, "test")}.{Sentence(T(item, "finding"), "Finding: ")}{Sentence(T(item, "note"))}", item)));
      }
      foreach (var item in ClinicalManual.Items(diagnosis, "differentials"))
      {
        blocks.Add(new("diagnosis", "Differential diagnoses", T(item, "condition"),
          WithRefs($"- {T(item, "condition")}.{Sentence(T(item, "distinguish"), "How to distinguish: ")}", item)));
      }
      foreach (var item in ClinicalManual.Items(diagnosis, "grading"))
        blocks.Add(new("diagnosis", "Grading", T(item, "grade"), WithRefs($"- {T(item, "grade")}: {T(item, "criteria")}", item)));

      // ---- approach ----
      foreach (var step in ClinicalManual.Items(root, "approach"))
      {
        var setting = T(step, "setting") is { Length: > 0 } s ? $" ({s})" : "";
        blocks.Add(new("approach", "", T(step, "action"), $"{T(step, "step")}. {T(step, "action")}{setting}.{Sentence(T(step, "detail"))}"));
      }

      // ---- treatments ----
      var treatments = new List<string>();
      foreach (var treatment in ClinicalManual.Items(root, "treatments"))
      {
        treatments.Add(T(treatment, "name"));
        blocks.Add(new("treatments", "", T(treatment, "name"), Treatment(treatment)));
      }

      // ---- prognosis ----
      var prognosis = root["prognosis"];
      if (T(prognosis, "text") is { Length: > 0 } prognosisText)
        blocks.Add(new("prognosis", "", "Prognosis", prognosisText));
      foreach (var item in ClinicalManual.Items(prognosis, "indicators"))
        blocks.Add(new("prognosis", "Prognostic indicators", T(item, "finding"), WithRefs($"- {T(item, "finding")}: {T(item, "meaning")}", item)));

      // ---- gaps ----
      foreach (var gap in ClinicalManual.Items(root, "evidence_gaps"))
        blocks.Add(new("gaps", "What is not known", "Evidence gap", $"- {gap}"));
      if (root["search"] is JsonObject search)
      {
        var sources = string.Join(", ", ClinicalManual.Items(search, "sources").Select(source => source.ToString()));
        blocks.Add(new("gaps", "Literature search behind this page", "Literature search",
          $"Searched on {T(search, "date")} in: {sources}.{Sentence(T(search, "note"))}"));
      }

      // ---- references ----
      var references = new Dictionary<string, string>(StringComparer.Ordinal);
      foreach (var reference in ClinicalManual.Items(root, "references"))
      {
        var key = T(reference, "ref");
        if (key.Length == 0)
          continue;
        references[key] = ShortReference(key, reference);
        blocks.Add(new("references", "", key, FullReference(key, reference)));
      }

      return new ClinicalPage(
        T(root, "id") is { Length: > 0 } pageId ? pageId : id, group, T(root, "title"), T(root, "updated"),
        definition, treatments, blocks, references);
    }

    private static string Treatment(JsonNode treatment)
    {
      var text = new StringBuilder();
      text.Append("\n### ").Append(T(treatment, "name")).Append('\n');
      text.Append("Class: ").Append(Or(T(treatment, "class"), "not stated"))
        .Append(". Status: ").Append(Or(T(treatment, "status"), "not stated"))
        .Append(". Evidence level: ").Append(Or(T(treatment, "evidence_level"), "not stated"));
      if (T(treatment, "independent_studies") is { Length: > 0 } studies)
        text.Append(" (").Append(studies).Append(" independent studies)");
      text.Append(".\n");

      Line(text, "Aim", T(treatment, "aim"));
      Line(text, "Evidence", T(treatment, "evidence_summary"));

      var doses = ClinicalManual.Items(treatment, "doses").ToList();
      if (doses.Count > 0)
      {
        text.Append("Doses:\n");
        foreach (var dose in doses)
        {
          var regimen = string.Join(", ", new[] { T(dose, "route"), T(dose, "frequency"), T(dose, "duration") }.Where(p => p.Length > 0));
          text.Append(WithRefs(
            $"- {T(dose, "drug")} {T(dose, "dose")}{(regimen.Length > 0 ? " " + regimen : "")}.{Sentence(T(dose, "context"), "Context: ")}{Sentence(T(dose, "note"))}",
            dose)).Append('\n');
        }
      }
      else
      {
        text.Append("Doses: none given on the page.\n");
      }

      Line(text, "Cautions", T(treatment, "cautions"));
      Line(text, "Monitoring", T(treatment, "monitoring"));
      Line(text, "Availability in South Africa", T(treatment, "availability"));
      return WithRefs(text.ToString().TrimEnd(), treatment);
    }

    /// <summary>One line for the list under a section: enough to weigh and to find the source.</summary>
    private static string ShortReference(string key, JsonNode reference)
    {
      var text = new StringBuilder($"{key}: {T(reference, "authors")} {T(reference, "year")}".TrimEnd());
      if (T(reference, "journal") is { Length: > 0 } journal)
        text.Append(", ").Append(journal);
      text.Append('.').Append(ReferenceFacts(reference));
      return text.ToString();
    }

    private static string FullReference(string key, JsonNode reference)
    {
      var journal = string.Join(" ", new[] { T(reference, "journal"), T(reference, "volume_pages") }.Where(p => p.Length > 0));
      return $"{key}: {T(reference, "authors")} ({T(reference, "year")}). {T(reference, "title").TrimEnd('.')}.{Sentence(journal)}{ReferenceFacts(reference)}";
    }

    /// <summary>The kind of source, its size, how it was read, its identifier and its review code.</summary>
    private static string ReferenceFacts(JsonNode reference)
    {
      var facts = new List<string>();
      if (T(reference, "type") is { Length: > 0 } type)
        facts.Add(type);
      if (T(reference, "species") is { Length: > 0 } species)
        facts.Add(species);
      if (T(reference, "n_dogs") is { Length: > 0 } dogs)
        facts.Add($"{dogs} dogs");
      if (T(reference, "read") is { Length: > 0 } read)
        facts.Add($"read as {read}");

      var text = new StringBuilder();
      if (facts.Count > 0)
        text.Append(' ').Append(char.ToUpperInvariant(facts[0][0])).Append(string.Join("; ", facts)[1..]).Append('.');

      if (T(reference, "doi") is { Length: > 0 } doi)
        text.Append(" https://doi.org/").Append(doi);
      else if (T(reference, "pmid") is { Length: > 0 } pmid)
        text.Append(" https://pubmed.ncbi.nlm.nih.gov/").Append(pmid).Append('/');
      else if (T(reference, "url") is { Length: > 0 } url)
        text.Append(' ').Append(url);

      if (T(reference, "article_id") is { Length: > 0 } article)
        text.Append(" In the review as ").Append(article).Append('.');
      return text.ToString();
    }

    private static string T(JsonNode? node, string name) => ClinicalManual.Text(node, name);

    private static string Or(string value, string fallback) => value.Length > 0 ? value : fallback;

    /// <summary>" Prefix value." or nothing, so optional fields join into one paragraph.</summary>
    private static string Sentence(string value, string prefix = "")
    {
      if (value.Length == 0)
        return "";
      return $" {prefix}{value}{(value[^1] is '.' or ']' or '!' or '?' ? "" : ".")}";
    }

    private static void Line(StringBuilder text, string label, string value)
    {
      if (value.Length > 0)
        text.Append(label).Append(": ").Append(value).Append('\n');
    }

    /// <summary>Adds the markers of the item's <c>refs</c> that its text does not already carry.</summary>
    private static string WithRefs(string text, JsonNode item)
    {
      var missing = ClinicalManual.Items(item, "refs")
        .Select(reference => reference.ToString())
        .Where(key => key.Length > 0 && !text.Contains($"[{key}]", StringComparison.Ordinal))
        .ToList();
      return missing.Count == 0 ? text : $"{text} {string.Concat(missing.Select(key => $"[{key}]"))}";
    }

    private static readonly IReadOnlyDictionary<string, string> SectionTitles = new Dictionary<string, string>
    {
      ["overview"] = "Overview",
      ["diagnosis"] = "Diagnosis",
      ["approach"] = "Approach, step by step (practice = a general practice can do it; referral = needs a referral hospital)",
      ["treatments"] = "Treatments",
      ["prognosis"] = "Prognosis",
      ["gaps"] = "Evidence gaps",
      ["references"] = "References"
    };

    private const string TreatmentLegend =
      "Evidence levels: A = a controlled trial in dogs with babesiosis; B = a cohort or a case series of five or more dogs " +
      "with babesiosis; C = case reports, or fewer than five dogs with babesiosis; D = extrapolated from the same syndrome " +
      "of another cause in dogs, or from humans; E = expert opinion, a textbook or a product label. " +
      "Status: standard = accepted practice in the sources; proposed = suggested or used in some dogs, not established; " +
      "conflicting = studies disagree; no_benefit = studied, no benefit found; harmful = reported to cause harm, or contraindicated.";

    [GeneratedRegex(@"\[(R\d+)\]")]
    private static partial Regex ReferenceMarker();
  }
}
