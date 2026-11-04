using Babesiosis.Core.Models.Domain;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Reference
{
  public class CountryConfig : IEntityTypeConfiguration<Country>
  {
    public void Configure(EntityTypeBuilder<Country> builder)
    {
      builder.ToTable("Country", "reference");
      builder.HasKey(e => e.Id).IsClustered();
    }
  }
}
