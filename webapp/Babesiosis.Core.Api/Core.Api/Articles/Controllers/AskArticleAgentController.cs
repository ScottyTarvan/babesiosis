using Babesiosis.Agents;
using Babesiosis.Agents.Articles;
using Babesiosis.Agents.OpenRouter;
using Babesiosis.Core.Api.Articles.Commands;
using Babesiosis.Core.Api.Articles.ViewModels;
using Babesiosis.Core.Articles.Data;
using Babesiosis.Core.Data;
using Babesiosis.Core.Exceptions;
using Microsoft.EntityFrameworkCore;
using System;
using System.ClientModel;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Api.Articles.Controllers
{
  /// <summary>
  /// Asks the article agent (Babesiosis.Agents) a question and shapes its answer for the web
  /// app's AI agent screen. The agent searches the article embeddings and answers through an
  /// OpenRouter model; this controller validates the request, turns configuration and
  /// provider failures into coded errors, and resolves each citation's source link the same
  /// way the Articles list does.
  /// </summary>
  public class AskArticleAgentController
  {
    public const string AgentUnavailable = "AI_AGENT_UNAVAILABLE";
    public const string AgentFailed = "AI_AGENT_FAILED";

    private readonly IArticleQuestionAgent _agent;
    private readonly IDbContextService _dbContextService;

    public AskArticleAgentController(IArticleQuestionAgent agent, IDbContextService dbContextService)
    {
      _agent = agent;
      _dbContextService = dbContextService;
    }

    public async Task<ArticleAgentAnswerViewModel> HandleCommand(Guid userId, AskArticleAgentCommand command,
      CancellationToken cancellationToken = default)
    {
      if (string.IsNullOrWhiteSpace(command?.Question))
      {
        throw new ValidationException("A question is required.");
      }

      var tier = AgentModelTier.Medium;
      if (!string.IsNullOrWhiteSpace(command.Tier)
        && (!Enum.TryParse(command.Tier.Trim(), ignoreCase: true, out tier) || !Enum.IsDefined(tier)))
      {
        throw new ValidationException($"Unknown tier '{command.Tier}'. Use Low, Medium, High or Max.");
      }

      ArticleAnswer answer;
      try
      {
        answer = await _agent.AskAsync(
          new ArticleQuestion(command.Question, tier, string.IsNullOrWhiteSpace(command.Conversation) ? null : command.Conversation),
          cancellationToken);
      }
      catch (AgentConfigurationException ex)
      {
        throw new CodedValidationException(AgentUnavailable, ex.Message, statusCode: 503);
      }
      catch (ArgumentException ex)
      {
        throw new ValidationException(ex.Message);
      }
      catch (ClientResultException ex)
      {
        // OpenRouter refused or failed the call: bad key, no credit, model unavailable, rate limit.
        throw new CodedValidationException(AgentFailed,
          $"The AI model could not answer (OpenRouter returned {ex.Status}). Try again shortly.", statusCode: 502);
      }

      return new ArticleAgentAnswerViewModel
      {
        Message = new ArticleAgentMessageViewModel
        {
          Id = Guid.NewGuid().ToString(),
          Role = "assistant",
          Content = answer.Answer,
          CreatedAt = DateTimeOffset.UtcNow,
          Citations = await ToCitationsAsync(answer, cancellationToken)
        },
        Conversation = answer.Conversation,
        Model = answer.Model,
        InputTokens = answer.InputTokens,
        OutputTokens = answer.OutputTokens
      };
    }

    /// <summary>The cited articles with their source links, resolved as in the Articles list.</summary>
    private async Task<List<ArticleAgentCitationViewModel>> ToCitationsAsync(
      ArticleAnswer answer, CancellationToken cancellationToken)
    {
      if (answer.Sources.Count == 0)
      {
        return new List<ArticleAgentCitationViewModel>();
      }

      var ids = answer.Sources.Select(s => s.ArticleId).ToList();

      using var dbContext = _dbContextService.CreateDbContext<ArticlesDbContext>();
      var links = await dbContext.Articles
        .AsNoTracking()
        .Where(a => ids.Contains(a.Id))
        .Select(a => new { a.Id, a.FulltextUrl, a.SourceLinks })
        .ToDictionaryAsync(a => a.Id, cancellationToken);

      return answer.Sources
        .Select(s =>
        {
          var link = links.GetValueOrDefault(s.ArticleId);
          return new ArticleAgentCitationViewModel
          {
            ArticleId = s.ArticleId,
            Code = s.Code,
            Title = s.Title,
            Year = s.Year,
            SourceUrl = ArticleSourceLink.Resolve(s.Doi, s.Pmid, link?.SourceLinks, link?.FulltextUrl),
            HasFullText = s.HasFullText,
            SectionsRead = s.SectionsRead.ToList()
          };
        })
        .ToList();
    }
  }
}
