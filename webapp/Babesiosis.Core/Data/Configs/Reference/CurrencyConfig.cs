using Babesiosis.Core.Models.Domain;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace Babesiosis.Core.Data.Configs.Reference
{
  public class CurrencyConfig : IEntityTypeConfiguration<Currency>
  {
    public void Configure(EntityTypeBuilder<Currency> builder)
    {
      builder.ToTable("Currency", "reference");
      builder.HasKey(e => e.Id).IsClustered();
    }
  }
}
