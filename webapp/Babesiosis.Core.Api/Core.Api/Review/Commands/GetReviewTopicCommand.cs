namespace Babesiosis.Core.Api.Review.Commands
{
  /// <summary>Loads one topic page.</summary>
  public class GetReviewTopicCommand
  {
    /// <summary>A category code, e.g. REN.</summary>
    public string Code { get; set; }
  }
}
