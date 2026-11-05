using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Api.Articles.ViewModels
{
  /// <summary>
  /// The article agent's answer. <see cref="Message"/> has the shape of the web app's
  /// <c>ChatMessageViewModel</c> (modules/ai-agent), so it can be appended to the thread as is.
  /// </summary>
  public class ArticleAgentAnswerViewModel
  {
    public ArticleAgentMessageViewModel Message { get; set; }

    /// <summary>Opaque state to send back as <c>conversation</c> with the next question.</summary>
    public string Conversation { get; set; }

    /// <summary>The OpenRouter model id that answered.</summary>
    public string Model { get; set; }

    public long? InputTokens { get; set; }
    public long? OutputTokens { get; set; }
  }

  public class ArticleAgentMessageViewModel
  {
    public string Id { get; set; }

    /// <summary>Always "assistant".</summary>
    public string Role { get; set; }

    /// <summary>Markdown, with article codes cited in square brackets, e.g. [CB024].</summary>
    public string Content { get; set; }

    /// <summary>ISO 8601 timestamp.</summary>
    public DateTimeOffset CreatedAt { get; set; }

    /// <summary>The articles the answer cites, in order of first citation.</summary>
    public List<ArticleAgentCitationViewModel> Citations { get; set; }
  }

  public class ArticleAgentCitationViewModel
  {
    public int ArticleId { get; set; }

    /// <summary>The review code, e.g. CB040.</summary>
    public string Code { get; set; }

    public string Title { get; set; }
    public int? Year { get; set; }

    /// <summary>Where to open the article; see <see cref="ArticleSourceLink"/>. Null when none is known.</summary>
    public string SourceUrl { get; set; }

    /// <summary>Whether the paper's own full text is in the database (dbo.article_section).</summary>
    public bool HasFullText { get; set; }

    /// <summary>
    /// The sections of the paper's own text the agent read for this answer (methods, results, ...).
    /// Empty when the answer rests on the review's record only.
    /// </summary>
    public List<string> SectionsRead { get; set; }
  }
}
