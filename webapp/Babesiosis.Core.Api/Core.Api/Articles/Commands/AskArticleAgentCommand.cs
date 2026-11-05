namespace Babesiosis.Core.Api.Articles.Commands
{
  /// <summary>One question to the article agent.</summary>
  public class AskArticleAgentCommand
  {
    /// <summary>The user's question, at most 4,000 characters.</summary>
    public string Question { get; set; }

    /// <summary>
    /// Optional model tier: Low, Medium, High or Max (case-insensitive). Each maps to an
    /// OpenRouter model in <c>AppSettings:AiAgents:Models</c>. Defaults to Medium.
    /// </summary>
    public string Tier { get; set; }

    /// <summary>
    /// The <c>conversation</c> value from the previous answer, to ask a follow-up. Omit it to
    /// start a new conversation.
    /// </summary>
    public string Conversation { get; set; }
  }
}
