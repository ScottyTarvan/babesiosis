using Babesiosis.Core.Data;
using Babesiosis.Core.Data.Configs.Articles;
using Babesiosis.Core.Models.Articles;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Articles.Data
{
  public class ArticlesDbContext : DbContextBase
  {
    public ArticlesDbContext(DbContextOptions options) : base(options)
    {
      //nop
    }

    public ArticlesDbContext(DbContextOptions options, IDbContextQuery query) : base(options, query)
    {
      //nop
    }

    public DbSet<Article> Articles { get; set; }
    public DbSet<Category> Categories { get; set; }
    public DbSet<ArticleCategory> ArticleCategories { get; set; }
    public DbSet<Term> Terms { get; set; }
    public DbSet<ArticleTerm> ArticleTerms { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
      base.OnModelCreating(modelBuilder);

      modelBuilder.ApplyConfiguration(new CategoryConfig());
      modelBuilder.ApplyConfiguration(new ArticleConfig());
      modelBuilder.ApplyConfiguration(new ArticleCategoryConfig());
      modelBuilder.ApplyConfiguration(new TermConfig());
      modelBuilder.ApplyConfiguration(new ArticleTermConfig());
    }
  }
}
