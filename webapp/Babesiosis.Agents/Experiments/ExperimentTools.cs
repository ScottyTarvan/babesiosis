using System.Collections.Concurrent;
using System.ComponentModel;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using Microsoft.Extensions.AI;

namespace Babesiosis.Agents.Experiments
{
  /// <summary>
  /// The functions the agent can call over the experiments (<see cref="ExperimentRepository"/>):
  /// the list of runs, one run with its interpretation, and one result payload. One instance
  /// serves one question and records the experiments the tools returned.
  /// </summary>
  internal sealed class ExperimentTools
  {
    /// <summary>Characters of JSON per get_experiment_result call; longer payloads come in parts.</summary>
    public const int ResultPartChars = 12_000;

    /// <summary>Settings that are provenance, not method: file hashes, input lists, tool versions.</summary>
    private static readonly string[] ProvenanceKeys = ["sha256", "inputs", "reports", "versions", "salt", "handover"];

    private readonly ExperimentRepository _repository;
    private readonly ConcurrentDictionary<string, byte> _seen = new(StringComparer.OrdinalIgnoreCase);
    private IReadOnlyList<ExperimentHeader>? _all;

    public ExperimentTools(ExperimentRepository repository)
    {
      _repository = repository;
    }

    /// <summary>How many distinct experiments the tools have returned so far.</summary>
    public int SeenCount => _seen.Count;

    public IList<AITool> AsTools() =>
    [
      AIFunctionFactory.Create(ListExperimentsAsync, "list_experiments"),
      AIFunctionFactory.Create(GetExperimentAsync, "get_experiment"),
      AIFunctionFactory.Create(GetExperimentResultAsync, "get_experiment_result")
    ];

    /// <summary>Every experiment, read once per question.</summary>
    public async Task<IReadOnlyList<ExperimentHeader>> AllAsync(CancellationToken cancellationToken) =>
      _all ??= await _repository.ListAsync(cancellationToken);

    [Description(
      "The experiments that were run in this project: its own analyses of the public datasets " +
      "and of the review's literature, on why some dogs develop severe babesiosis. Returns one " +
      "row per experiment with its code, package (experiments of one package answer one " +
      "question), name, method, role (primary, replication, sensitivity or descriptive), " +
      "datasets, number of dogs and tests, the question it asked and a summary of its result. " +
      "An experiment with the method integration_synthesis draws the others together: read it " +
      "first for a question about the experiments as a whole. Call get_experiment for the full " +
      "explanation of one experiment.")]
    private async Task<ExperimentList> ListExperimentsAsync(
      [Description("Optional package to list, e.g. \"SV-05\". Empty = all packages.")]
      string? package = null,
      CancellationToken cancellationToken = default)
    {
      var all = await AllAsync(cancellationToken);
      if (all.Count == 0)
        return new ExperimentList(0, 0, [], "No experiment is loaded in the database.");

      var wanted = string.IsNullOrWhiteSpace(package) ? null : package.Trim();
      var listed = wanted is null
        ? all
        : all.Where(e => e.Package.Equals(wanted, StringComparison.OrdinalIgnoreCase)).ToList();

      string? note = null;
      if (listed.Count == 0)
      {
        note = $"No package \"{wanted}\". The packages are: {string.Join(", ", all.Select(e => e.Package).Distinct())}. All experiments are listed.";
        listed = all;
      }

      foreach (var experiment in listed)
        _seen.TryAdd(experiment.Code, 0);

      return new ExperimentList(
        listed.Count,
        listed.Select(e => e.Package).Distinct(StringComparer.OrdinalIgnoreCase).Count(),
        listed.Select(e => new ExperimentSummary(
          e.Code, e.Package, e.Name, e.Method, e.Role, e.Datasets, RunDate(e), e.Subjects, e.Tests, e.Description, e.Summary)).ToList(),
        note);
    }

    [Description(
      "One experiment in full: the question and hypothesis, the method, role, datasets and " +
      "independent sources, the settings of the run, the summary of the result, and the " +
      "interpretation written with the run (Question, What was done, Result, What this does " +
      "not show). Also lists the experiment's result tables by kind and size; read one with " +
      "get_experiment_result when the interpretation does not give the numbers you need.")]
    private async Task<ExperimentReport> GetExperimentAsync(
      [Description("The experiment code from list_experiments, e.g. \"SV-05-01-age-death\". The short form \"SV-05-01\" also works.")]
      string code,
      CancellationToken cancellationToken = default)
    {
      var (resolved, problem) = await ResolveAsync(code, cancellationToken);
      if (resolved is null)
        return ExperimentReport.Missing(code, problem!);

      var record = await _repository.GetAsync(resolved, cancellationToken);
      if (record is null)
        return ExperimentReport.Missing(code, $"Experiment {resolved} is no longer in the database.");

      _seen.TryAdd(resolved, 0);
      var header = record.Header;

      return new ExperimentReport(
        header.Code, header.Package, header.Name, header.Method, header.Role, header.Datasets, header.IndependentSources,
        RunDate(header), header.Subjects, header.Variables, header.Tests, header.Description, header.Summary,
        Settings(header.Parameters),
        InterpretationText(record.Interpretation),
        record.Results.Where(r => r.Kind != ExperimentRepository.InterpretationKind).ToList(),
        record.Interpretation is null ? "This experiment has no interpretation text; read its results." : null);
    }

    [Description(
      "One result of an experiment as JSON: a table of tests, the primary result with its " +
      "effect size and interval, a list of findings, or the points of a chart. Use the kinds " +
      "that get_experiment lists. Returns at most 12,000 characters at a time; a longer result " +
      "says how many parts there are, and you call again with the next part. Chart data " +
      "(many points) is rarely worth reading: prefer the tables and the primary result.")]
    private async Task<ExperimentResultPart> GetExperimentResultAsync(
      [Description("The experiment code, e.g. \"SV-05-01-age-death\".")]
      string code,
      [Description("The result kind from get_experiment, e.g. \"primary_result\" or \"tests_table\".")]
      string kind,
      [Description("Which part of a long result to return, from 1. Default 1.")]
      int part = 1,
      CancellationToken cancellationToken = default)
    {
      var (resolved, problem) = await ResolveAsync(code, cancellationToken);
      if (resolved is null)
        return new ExperimentResultPart(code?.Trim() ?? "", kind ?? "", null, 1, 0, "", problem);

      var wanted = (kind ?? "").Trim().ToLowerInvariant().Replace(' ', '_').Replace('-', '_');
      var payload = wanted.Length == 0 ? null : await _repository.GetPayloadAsync(resolved, wanted, cancellationToken);
      if (payload is null)
      {
        var record = await _repository.GetAsync(resolved, cancellationToken);
        var kinds = record is null ? "" : string.Join(", ", record.Results.Select(r => r.Kind));
        return new ExperimentResultPart(resolved, wanted, null, 1, 0, "", $"{resolved} has no result of the kind \"{kind}\". Its kinds are: {kinds}.");
      }

      _seen.TryAdd(resolved, 0);

      var json = DescribeFigure(payload.Json, out var figureNote);
      var parts = Math.Max(1, (int)Math.Ceiling(json.Length / (double)ResultPartChars));
      if (part < 1 || part > parts)
        return new ExperimentResultPart(resolved, payload.Kind, payload.Title, part, parts, "", $"part must be between 1 and {parts}.");

      var start = (part - 1) * ResultPartChars;
      var text = json.Substring(start, Math.Min(ResultPartChars, json.Length - start));
      var note = figureNote ?? (parts > 1
        ? part < parts
          ? $"Part {part} of {parts}: the JSON is cut at a character count, not at a row. Call again with part = {part + 1} for the rest."
          : $"Part {part} of {parts}: the end of the result."
        : null);

      return new ExperimentResultPart(resolved, payload.Kind, payload.Title, part, parts, text, note);
    }

    /// <summary>
    /// The experiment the model means: its exact code, or the one code that starts with what
    /// it gave ("SV-05-01"). Otherwise a message that lists the codes, which the model can act on.
    /// </summary>
    private async Task<(string? Code, string? Problem)> ResolveAsync(string? code, CancellationToken cancellationToken)
    {
      var all = await AllAsync(cancellationToken);
      var given = (code ?? "").Trim();
      if (given.Length == 0)
        return (null, $"code is required. The experiments are: {string.Join(", ", all.Select(e => e.Code))}.");

      var exact = all.FirstOrDefault(e => e.Code.Equals(given, StringComparison.OrdinalIgnoreCase));
      if (exact is not null)
        return (exact.Code, null);

      var starting = all.Where(e => e.Code.StartsWith(given, StringComparison.OrdinalIgnoreCase)).ToList();
      return starting.Count switch
      {
        1 => (starting[0].Code, null),
        0 => (null, $"No experiment has the code \"{given}\". The experiments are: {string.Join(", ", all.Select(e => e.Code))}."),
        _ => (null, $"\"{given}\" matches {starting.Count} experiments: {string.Join(", ", starting.Select(e => e.Code))}. Use one full code.")
      };
    }

    private static string? RunDate(ExperimentHeader header) => header.RunAt?.ToString("yyyy-MM-dd");

    /// <summary>The interpretation payload (<c>{"sections":[{"heading","paragraphs"}]}</c>) as Markdown.</summary>
    private static string? InterpretationText(string? payload)
    {
      if (string.IsNullOrWhiteSpace(payload))
        return null;

      try
      {
        if (JsonNode.Parse(payload)?["sections"] is not JsonArray sections)
          return payload;

        var text = new StringBuilder();
        foreach (var section in sections)
        {
          if (section?["heading"] is JsonValue heading)
            text.Append("### ").Append(heading.ToString()).Append('\n');
          if (section?["paragraphs"] is JsonArray paragraphs)
          {
            foreach (var paragraph in paragraphs.Where(p => p is not null))
              text.Append(paragraph!.ToString()).Append("\n\n");
          }
        }
        return text.ToString().TrimEnd();
      }
      catch (JsonException)
      {
        return payload;
      }
    }

    /// <summary>
    /// The run's settings without provenance (hashes, input file lists, tool versions) and
    /// without what the header already gives, as compact JSON. Null when nothing is left.
    /// </summary>
    private static string? Settings(string? parameters)
    {
      if (string.IsNullOrWhiteSpace(parameters))
        return null;

      try
      {
        if (JsonNode.Parse(parameters) is not JsonObject root)
          return null;

        var kept = new JsonObject();
        foreach (var (name, value) in root)
        {
          if (value is null
            || name is "package" or "role" or "datasets" or "independent_sources"
            || ProvenanceKeys.Any(key => name.Contains(key, StringComparison.OrdinalIgnoreCase)))
          {
            continue;
          }

          var json = value.ToJsonString();
          if (json.Length <= 600)
            kept[name] = JsonNode.Parse(json);
        }

        return kept.Count == 0 ? null : kept.ToJsonString();
      }
      catch (JsonException)
      {
        return null;
      }
    }

    /// <summary>
    /// A figure payload (<c>{"mime","base64","alt","caption"}</c>) is an image the model cannot
    /// read: its description is returned in place of the image data.
    /// </summary>
    private static string DescribeFigure(string json, out string? note)
    {
      note = null;
      if (!json.Contains("\"base64\"", StringComparison.Ordinal))
        return json;

      try
      {
        if (JsonNode.Parse(json) is JsonObject figure && figure.ContainsKey("base64"))
        {
          figure.Remove("base64");
          note = "This result is an image. Only its description (alt, caption) is given; the numbers behind it are in the experiment's other results.";
          return figure.ToJsonString();
        }
      }
      catch (JsonException)
      {
        // Not a figure object: return the payload as it is.
      }

      return json;
    }
  }

  /// <summary>One row of list_experiments.</summary>
  /// <param name="Question">The question and the hypothesis.</param>
  /// <param name="Summary">The primary result with its effect size, interval and n.</param>
  public sealed record ExperimentSummary(
    string Code, string Package, string Name, string Method, string? Role, IReadOnlyList<string> Datasets,
    string? RunDate, int? Dogs, int? Tests, string? Question, string? Summary);

  /// <param name="Count">How many experiments are listed: given so the model does not count them itself.</param>
  /// <param name="Packages">How many packages they belong to.</param>
  public sealed record ExperimentList(int Count, int Packages, IReadOnlyList<ExperimentSummary> Experiments, string? Note);

  /// <summary>One experiment, from get_experiment.</summary>
  /// <param name="Settings">The settings of the run as JSON, without file hashes and input lists.</param>
  /// <param name="Interpretation">The explanation written with the run, as Markdown.</param>
  /// <param name="Results">The result tables that get_experiment_result can return.</param>
  /// <param name="Note">Why there is no experiment or no interpretation; otherwise null.</param>
  public sealed record ExperimentReport(
    string Code, string? Package, string? Name, string? Method, string? Role,
    IReadOnlyList<string> Datasets, IReadOnlyList<string> IndependentSources,
    string? RunDate, int? Dogs, int? Variables, int? Tests, string? Question, string? Summary,
    string? Settings, string? Interpretation, IReadOnlyList<ExperimentResultInfo> Results, string? Note)
  {
    public static ExperimentReport Missing(string? code, string note) =>
      new(code?.Trim() ?? "", null, null, null, null, [], [], null, null, null, null, null, null, null, null, [], note);
  }

  /// <summary>One part of a result's JSON, from get_experiment_result.</summary>
  /// <param name="Parts">How many parts the JSON comes in; 0 when there is no result (see <paramref name="Note"/>).</param>
  public sealed record ExperimentResultPart(
    string Code, string Kind, string? Title, int Part, int Parts, string Json, string? Note);
}
