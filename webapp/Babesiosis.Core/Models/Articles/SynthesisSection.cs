using System;

namespace Babesiosis.Core.Models.Articles
{
  /// <summary>
  /// One headed section of a narrative synthesis (dbo.synthesis_section): a category file
  /// (core/search/synthesis/&lt;CODE&gt;.md), CROSS.md or QUESTIONS.md, as written (Markdown).
  /// Loaded by Babesiosis.Console --synthesis-only.
  /// </summary>
  public class SynthesisSection
  {
    public int Id { get; set; }
    /// <summary>A category code (ERY .. SEV), CROSS or QUESTIONS.</summary>
    public string DocumentCode { get; set; }
    public short SectionOrder { get; set; }
    /// <summary>e.g. question-this-direction-asks, theme-1, q1, intro.</summary>
    public string SectionKey { get; set; }
    public string Heading { get; set; }
    public string Body { get; set; }
    public string SourceFile { get; set; }
    /// <summary>UTC, the file's last write time when it was loaded.</summary>
    public DateTime FileModifiedAt { get; set; }
    /// <summary>UTC.</summary>
    public DateTime LoadedAt { get; set; }
  }
}
