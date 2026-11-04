namespace Babesiosis.Core.Models.Articles
{
  /// <summary>
  /// A secondary or comparator category tag on an article (dbo.article_category).
  /// The primary category is held on <see cref="Article.PrimaryCategoryId"/>, not here.
  /// </summary>
  public class ArticleCategory
  {
    public int ArticleId { get; set; }
    public int CategoryId { get; set; }
    public ArticleTagType TagType { get; set; }

    public virtual Article Article { get; set; }
    public virtual Category Category { get; set; }
  }
}
