using Babesiosis.Core.Data;
using Babesiosis.Core.Data.Configs.Articles;
using Babesiosis.Core.Data.Configs.Experiments;
using Babesiosis.Core.Models.Articles;
using Babesiosis.Core.Models.Experiments;
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
    /// <summary>The narrative syntheses, split by heading (console --synthesis-only).</summary>
    public DbSet<SynthesisSection> SynthesisSections { get; set; }

    // The tidied datasets and the experiments run over them (console --datasets-only).
    public DbSet<Dataset> Datasets { get; set; }
    public DbSet<Variable> Variables { get; set; }
    public DbSet<Subject> Subjects { get; set; }
    public DbSet<Observation> Observations { get; set; }
    public DbSet<Experiment> Experiments { get; set; }
    public DbSet<Association> Associations { get; set; }
    public DbSet<ExperimentResult> ExperimentResults { get; set; }
    public DbSet<ClusterAssignment> ClusterAssignments { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
      base.OnModelCreating(modelBuilder);

      modelBuilder.ApplyConfiguration(new CategoryConfig());
      modelBuilder.ApplyConfiguration(new ArticleConfig());
      modelBuilder.ApplyConfiguration(new ArticleCategoryConfig());
      modelBuilder.ApplyConfiguration(new TermConfig());
      modelBuilder.ApplyConfiguration(new ArticleTermConfig());
      modelBuilder.ApplyConfiguration(new SynthesisSectionConfig());

      modelBuilder.ApplyConfiguration(new DatasetConfig());
      modelBuilder.ApplyConfiguration(new VariableConfig());
      modelBuilder.ApplyConfiguration(new SubjectConfig());
      modelBuilder.ApplyConfiguration(new ObservationConfig());
      modelBuilder.ApplyConfiguration(new ExperimentConfig());
      modelBuilder.ApplyConfiguration(new AssociationConfig());
      modelBuilder.ApplyConfiguration(new ExperimentResultConfig());
      modelBuilder.ApplyConfiguration(new ClusterAssignmentConfig());
    }
  }
}
