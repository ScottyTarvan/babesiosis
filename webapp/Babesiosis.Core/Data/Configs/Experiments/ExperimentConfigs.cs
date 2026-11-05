using Babesiosis.Core.Models.Experiments;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Experiments
{
  // The eight experiment tables are one feature loaded by one console step, so their
  // configurations live together here (schema: console/Babesiosis.Console/Database/schema.sql).

  public class DatasetConfig : IEntityTypeConfiguration<Dataset>
  {
    public void Configure(EntityTypeBuilder<Dataset> builder)
    {
      builder.ToTable("dataset", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_dataset").IsClustered();

      builder.Property(e => e.Id).HasColumnName("dataset_id").UseIdentityColumn();
      builder.Property(e => e.Code).HasColumnName("dataset_code").HasMaxLength(20).IsUnicode(false).IsRequired();
      builder.Property(e => e.Title).HasColumnName("title").HasMaxLength(500).IsRequired();
      builder.Property(e => e.ArticleCode).HasColumnName("article_code").HasMaxLength(10).IsUnicode(false);
      builder.Property(e => e.ArticleId).HasColumnName("article_id");
      builder.Property(e => e.Repository).HasColumnName("repository").HasMaxLength(200);
      builder.Property(e => e.SourceRecord).HasColumnName("source_record").HasMaxLength(400);
      builder.Property(e => e.Licence).HasColumnName("licence").HasMaxLength(400);
      builder.Property(e => e.IndependentSource).HasColumnName("independent_source").HasMaxLength(10).IsUnicode(false);
      builder.Property(e => e.Species).HasColumnName("species").HasMaxLength(400);
      builder.Property(e => e.Design).HasColumnName("design");
      builder.Property(e => e.SourceFile).HasColumnName("source_file").HasMaxLength(300);
      builder.Property(e => e.SourceSha256).HasColumnName("source_sha256").HasMaxLength(64).IsUnicode(false).IsFixedLength();
      builder.Property(e => e.SubjectCount).HasColumnName("n_subjects");
      builder.Property(e => e.Notes).HasColumnName("notes").HasColumnType("json");
      builder.Property(e => e.ExtractedAt).HasColumnName("extracted_at").HasPrecision(0);
      builder.Property(e => e.LoadedAt).HasColumnName("loaded_at").HasPrecision(0);

      builder.HasIndex(e => e.Code).HasDatabaseName("UQ_dataset_code").IsUnique();
      builder.HasOne(e => e.Article).WithMany()
        .HasForeignKey(e => e.ArticleId)
        .HasConstraintName("FK_dataset_article")
        .OnDelete(DeleteBehavior.NoAction);
    }
  }

  public class VariableConfig : IEntityTypeConfiguration<Variable>
  {
    public void Configure(EntityTypeBuilder<Variable> builder)
    {
      builder.ToTable("variable", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_variable").IsClustered();

      builder.Property(e => e.Id).HasColumnName("variable_id").UseIdentityColumn();
      builder.Property(e => e.DatasetId).HasColumnName("dataset_id");
      builder.Property(e => e.Code).HasColumnName("variable_code").HasMaxLength(60).IsUnicode(false).IsRequired();
      builder.Property(e => e.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
      builder.Property(e => e.SourceName).HasColumnName("source_name").HasMaxLength(200);
      builder.Property(e => e.CanonicalCode).HasColumnName("canonical_code").HasMaxLength(60).IsUnicode(false);
      builder.Property(e => e.Unit).HasColumnName("unit").HasMaxLength(50);
      builder.Property(e => e.DataType).HasColumnName("data_type").HasMaxLength(1).IsUnicode(false).IsFixedLength().IsRequired();
      builder.Property(e => e.Domain).HasColumnName("domain").HasMaxLength(30).IsUnicode(false);
      builder.Property(e => e.Derived).HasColumnName("derived");
      builder.Property(e => e.DerivedFrom).HasColumnName("derived_from").HasColumnType("json");
      builder.Property(e => e.IncludeDefault).HasColumnName("include_default");
      builder.Property(e => e.RefLow).HasColumnName("ref_low");
      builder.Property(e => e.RefHigh).HasColumnName("ref_high");
      builder.Property(e => e.Description).HasColumnName("description").HasMaxLength(1000);
      builder.Property(e => e.Levels).HasColumnName("levels").HasColumnType("json");
      builder.Property(e => e.SortOrder).HasColumnName("sort_order");

      builder.HasIndex(e => new { e.DatasetId, e.Code }).HasDatabaseName("UQ_variable_dataset_code").IsUnique();
      builder.HasOne(e => e.Dataset).WithMany(e => e.Variables)
        .HasForeignKey(e => e.DatasetId)
        .HasConstraintName("FK_variable_dataset")
        .OnDelete(DeleteBehavior.Cascade);
    }
  }

  public class SubjectConfig : IEntityTypeConfiguration<Subject>
  {
    public void Configure(EntityTypeBuilder<Subject> builder)
    {
      builder.ToTable("subject", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_subject").IsClustered();

      builder.Property(e => e.Id).HasColumnName("subject_id").UseIdentityColumn();
      builder.Property(e => e.DatasetId).HasColumnName("dataset_id");
      builder.Property(e => e.Code).HasColumnName("subject_code").HasMaxLength(60).IsUnicode(false).IsRequired();
      builder.Property(e => e.GroupLabel).HasColumnName("group_label").HasMaxLength(100);
      builder.Property(e => e.OutcomeLabel).HasColumnName("outcome_label").HasMaxLength(100);

      builder.HasIndex(e => new { e.DatasetId, e.Code }).HasDatabaseName("UQ_subject_dataset_code").IsUnique();
      builder.HasOne(e => e.Dataset).WithMany(e => e.Subjects)
        .HasForeignKey(e => e.DatasetId)
        .HasConstraintName("FK_subject_dataset")
        .OnDelete(DeleteBehavior.Cascade);
    }
  }

  public class ObservationConfig : IEntityTypeConfiguration<Observation>
  {
    public void Configure(EntityTypeBuilder<Observation> builder)
    {
      builder.ToTable("observation", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_observation").IsClustered();

      builder.Property(e => e.Id).HasColumnName("observation_id").UseIdentityColumn();
      builder.Property(e => e.SubjectId).HasColumnName("subject_id");
      builder.Property(e => e.VariableId).HasColumnName("variable_id");
      builder.Property(e => e.TimePoint).HasColumnName("time_point").HasMaxLength(30).IsUnicode(false).IsRequired();
      builder.Property(e => e.ValueNum).HasColumnName("value_num");
      builder.Property(e => e.ValueText).HasColumnName("value_text").HasMaxLength(400);
      builder.Property(e => e.ValueDate).HasColumnName("value_date");

      builder.HasIndex(e => new { e.SubjectId, e.VariableId, e.TimePoint }).HasDatabaseName("UQ_observation").IsUnique();
      builder.HasIndex(e => e.VariableId).HasDatabaseName("IX_observation_variable");
      builder.HasOne(e => e.Subject).WithMany()
        .HasForeignKey(e => e.SubjectId)
        .HasConstraintName("FK_observation_subject")
        .OnDelete(DeleteBehavior.Cascade);
      builder.HasOne(e => e.Variable).WithMany()
        .HasForeignKey(e => e.VariableId)
        .HasConstraintName("FK_observation_variable")
        .OnDelete(DeleteBehavior.NoAction);
    }
  }

  public class ExperimentConfig : IEntityTypeConfiguration<Experiment>
  {
    public void Configure(EntityTypeBuilder<Experiment> builder)
    {
      builder.ToTable("experiment", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_experiment").IsClustered();

      builder.Property(e => e.Id).HasColumnName("experiment_id").UseIdentityColumn();
      builder.Property(e => e.Code).HasColumnName("experiment_code").HasMaxLength(60).IsUnicode(false).IsRequired();
      builder.Property(e => e.Name).HasColumnName("name").HasMaxLength(200).IsRequired();
      builder.Property(e => e.Description).HasColumnName("description");
      builder.Property(e => e.Method).HasColumnName("method").HasMaxLength(50).IsUnicode(false).IsRequired();
      builder.Property(e => e.DatasetId).HasColumnName("dataset_id");
      builder.Property(e => e.Parameters).HasColumnName("parameters").HasColumnType("json");
      builder.Property(e => e.Script).HasColumnName("script").HasMaxLength(200);
      builder.Property(e => e.ScriptVersion).HasColumnName("script_version").HasMaxLength(64).IsUnicode(false);
      builder.Property(e => e.RunAt).HasColumnName("run_at").HasPrecision(0);
      builder.Property(e => e.SubjectCount).HasColumnName("n_subjects");
      builder.Property(e => e.VariableCount).HasColumnName("n_variables");
      builder.Property(e => e.TestCount).HasColumnName("n_tests");
      builder.Property(e => e.Summary).HasColumnName("summary");
      builder.Property(e => e.LoadedAt).HasColumnName("loaded_at").HasPrecision(0);

      builder.HasIndex(e => e.Code).HasDatabaseName("UQ_experiment_code").IsUnique();
      builder.HasOne(e => e.Dataset).WithMany(e => e.Experiments)
        .HasForeignKey(e => e.DatasetId)
        .HasConstraintName("FK_experiment_dataset")
        .OnDelete(DeleteBehavior.NoAction);
    }
  }

  public class AssociationConfig : IEntityTypeConfiguration<Association>
  {
    public void Configure(EntityTypeBuilder<Association> builder)
    {
      builder.ToTable("association", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_association").IsClustered();

      builder.Property(e => e.Id).HasColumnName("association_id").UseIdentityColumn();
      builder.Property(e => e.ExperimentId).HasColumnName("experiment_id");
      builder.Property(e => e.VariableAId).HasColumnName("variable_a_id");
      builder.Property(e => e.VariableBId).HasColumnName("variable_b_id");
      builder.Property(e => e.Test).HasColumnName("test").HasMaxLength(30).IsUnicode(false).IsRequired();
      builder.Property(e => e.Estimate).HasColumnName("estimate");
      builder.Property(e => e.EstimateLabel).HasColumnName("estimate_label").HasMaxLength(30).IsUnicode(false);
      builder.Property(e => e.N).HasColumnName("n");
      builder.Property(e => e.PValue).HasColumnName("p_value");
      builder.Property(e => e.PAdjusted).HasColumnName("p_adjusted");
      builder.Property(e => e.Significant).HasColumnName("significant");
      builder.Property(e => e.Trivial).HasColumnName("trivial");
      builder.Property(e => e.Direction).HasColumnName("direction").HasMaxLength(200);
      builder.Property(e => e.Detail).HasColumnName("detail").HasColumnType("json");

      builder.HasIndex(e => new { e.ExperimentId, e.PAdjusted }).HasDatabaseName("IX_association_experiment");
      builder.HasOne(e => e.Experiment).WithMany(e => e.Associations)
        .HasForeignKey(e => e.ExperimentId)
        .HasConstraintName("FK_association_experiment")
        .OnDelete(DeleteBehavior.Cascade);
      builder.HasOne(e => e.VariableA).WithMany()
        .HasForeignKey(e => e.VariableAId)
        .HasConstraintName("FK_association_variable_a")
        .OnDelete(DeleteBehavior.NoAction);
      builder.HasOne(e => e.VariableB).WithMany()
        .HasForeignKey(e => e.VariableBId)
        .HasConstraintName("FK_association_variable_b")
        .OnDelete(DeleteBehavior.NoAction);
    }
  }

  public class ExperimentResultConfig : IEntityTypeConfiguration<ExperimentResult>
  {
    public void Configure(EntityTypeBuilder<ExperimentResult> builder)
    {
      builder.ToTable("experiment_result", "dbo");
      builder.HasKey(e => e.Id).HasName("PK_experiment_result").IsClustered();

      builder.Property(e => e.Id).HasColumnName("result_id").UseIdentityColumn();
      builder.Property(e => e.ExperimentId).HasColumnName("experiment_id");
      builder.Property(e => e.Kind).HasColumnName("result_kind").HasMaxLength(40).IsUnicode(false).IsRequired();
      builder.Property(e => e.Title).HasColumnName("title").HasMaxLength(200);
      builder.Property(e => e.Payload).HasColumnName("payload").HasColumnType("json").IsRequired();
      builder.Property(e => e.SortOrder).HasColumnName("sort_order");

      builder.HasIndex(e => new { e.ExperimentId, e.SortOrder }).HasDatabaseName("IX_experiment_result_experiment");
      builder.HasOne(e => e.Experiment).WithMany(e => e.Results)
        .HasForeignKey(e => e.ExperimentId)
        .HasConstraintName("FK_result_experiment")
        .OnDelete(DeleteBehavior.Cascade);
    }
  }

  public class ClusterAssignmentConfig : IEntityTypeConfiguration<ClusterAssignment>
  {
    public void Configure(EntityTypeBuilder<ClusterAssignment> builder)
    {
      builder.ToTable("cluster_assignment", "dbo");
      builder.HasKey(e => new { e.ExperimentId, e.SubjectId }).HasName("PK_cluster_assignment").IsClustered();

      builder.Property(e => e.ExperimentId).HasColumnName("experiment_id");
      builder.Property(e => e.SubjectId).HasColumnName("subject_id");
      builder.Property(e => e.ClusterLabel).HasColumnName("cluster_label").HasMaxLength(30).IsUnicode(false).IsRequired();
      builder.Property(e => e.Score).HasColumnName("score");

      builder.HasOne(e => e.Experiment).WithMany(e => e.ClusterAssignments)
        .HasForeignKey(e => e.ExperimentId)
        .HasConstraintName("FK_cluster_experiment")
        .OnDelete(DeleteBehavior.Cascade);
      builder.HasOne(e => e.Subject).WithMany()
        .HasForeignKey(e => e.SubjectId)
        .HasConstraintName("FK_cluster_subject")
        .OnDelete(DeleteBehavior.NoAction);
    }
  }
}
