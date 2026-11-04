using DevExtreme.AspNet.Data;

namespace Babesiosis.Core.Api.Articles.Commands
{
  /// <summary>
  /// Server-mode grid load for the Articles list: skip, take, sort and the
  /// filter row's expression, with selectors naming
  /// <see cref="ViewModels.ArticleViewModel"/> properties. A missing or zero
  /// <c>Take</c> falls back to the screen's page size.
  /// </summary>
  public class GetArticleListCommand
  {
    public DataSourceLoadOptionsBase LoadOptions { get; set; }
  }
}
