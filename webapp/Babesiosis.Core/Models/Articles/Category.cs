using System.Collections.Generic;

namespace Babesiosis.Core.Models.Articles
{
  /// <summary>One of the pathophysiology categories an article is classified under (dbo.category).</summary>
  public class Category
  {
    public int Id { get; set; }
    public string Code { get; set; }
    public string Name { get; set; }
    public string Label { get; set; }
    public byte SortOrder { get; set; }

    /// <summary>Articles whose primary category this is.</summary>
    public virtual ICollection<Article> PrimaryArticles { get; set; } = new List<Article>();

    /// <summary>Secondary and comparator tags that point at this category.</summary>
    public virtual ICollection<ArticleCategory> ArticleCategories { get; set; } = new List<ArticleCategory>();
  }
}
