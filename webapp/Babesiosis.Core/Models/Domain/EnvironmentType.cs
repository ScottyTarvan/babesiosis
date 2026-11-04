using System.ComponentModel;

namespace Babesiosis.Core.Models.Domain
{
  public enum EnvironmentType : short
  {
    None = 0,
    [Description("DEV")]
    DEV = 1,
    [Description("UAT")]
    UAT = 2,
    [Description("PRE-PROD")]
    PREPROD = 3,
    [Description("PROD")]
    PROD = 4,
  }
}
