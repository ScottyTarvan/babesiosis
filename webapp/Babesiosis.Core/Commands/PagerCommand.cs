using Babesiosis.Core.Models.Domain;

namespace Babesiosis.Core.Commands
{
  public class PagerCommand
  {
    public int Page { get; set; } = 1;
    public int PageSize { get; set; } = 25;
    public string SortBy { get; set; }
    public SortOrder SortOrder { get; set; }
    public int Skip { get; set; } = 0;
    public int Take { get; set; } = 25;
  }
}
