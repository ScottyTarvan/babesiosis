namespace Babesiosis.Core.Configurations.Configurations
{
  public class ExpectationsConfiguration
  {
    public int RetentionDays { get; set; } = 7;
    public int ExceptionRowCap { get; set; } = 500;
    public string Container { get; set; }
  }
}
