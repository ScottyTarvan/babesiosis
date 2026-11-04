using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.Api.Articles
{
  /// <summary>
  /// Where to send a reader who wants the article itself, outside this
  /// application. In order of preference: the publisher's page through the DOI,
  /// PubMed through the PMID, the first recorded source link that is a landing
  /// page rather than an index or API record, and last the recorded full-text
  /// file. Null when the article has none of these.
  /// </summary>
  public static class ArticleSourceLink
  {
    /// <summary>
    /// Hosts whose links are catalogue or API records of the article, not the
    /// article: OpenAlex (and its API), the Crossref API, DOAJ and the Europe
    /// PMC REST service. A link on one of these, or on any of their subdomains,
    /// is skipped.
    /// </summary>
    static readonly string[] IndexHosts = { "openalex.org", "api.crossref.org", "doaj.org", "ebi.ac.uk" };

    public static string Resolve(string doi, string pmid, string sourceLinksJson, string fulltextUrl)
    {
      if (!string.IsNullOrWhiteSpace(doi))
      {
        return "https://doi.org/" + doi.Trim();
      }

      if (!string.IsNullOrWhiteSpace(pmid))
      {
        return "https://pubmed.ncbi.nlm.nih.gov/" + pmid.Trim() + "/";
      }

      return ParseLinks(sourceLinksJson)
        .Append(fulltextUrl)
        .FirstOrDefault(IsLandingPage);
    }

    /// <summary>The recorded links, in their recorded order; empty when the JSON is missing or malformed.</summary>
    static IEnumerable<string> ParseLinks(string json)
    {
      if (string.IsNullOrWhiteSpace(json))
      {
        return Enumerable.Empty<string>();
      }

      try
      {
        return JsonConvert.DeserializeObject<List<string>>(json) ?? new List<string>();
      }
      catch (JsonException)
      {
        return Enumerable.Empty<string>();
      }
    }

    static bool IsLandingPage(string link)
    {
      if (string.IsNullOrWhiteSpace(link)
        || !Uri.TryCreate(link.Trim(), UriKind.Absolute, out var uri)
        || (uri.Scheme != Uri.UriSchemeHttp && uri.Scheme != Uri.UriSchemeHttps))
      {
        return false;
      }

      string host = uri.Host;
      return !IndexHosts.Any(index =>
        host.Equals(index, StringComparison.OrdinalIgnoreCase)
        || host.EndsWith("." + index, StringComparison.OrdinalIgnoreCase));
    }
  }
}
