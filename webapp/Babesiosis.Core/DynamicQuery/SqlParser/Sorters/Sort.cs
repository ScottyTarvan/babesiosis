namespace Babesiosis.Core.DynamicQuery.SqlParser.Sorters
{
  public class Sort : SqlGenerator
  {
    public string Name { get; set; }
    public bool Descending { get; set; }

    override public string CreateSql()
    {
      return $"{Name} {(Descending ? SortOrders.DESCENDING : SortOrders.ASCENDING)}";
    }

    override public string ToString()
    {
      return $"{Name} {(Descending ? SortOrders.DESCENDING : SortOrders.ASCENDING)}";
    }
  }
}
