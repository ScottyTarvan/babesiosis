using System.ComponentModel;

namespace Babesiosis.Core.Models.Teams
{
  public enum NotificationType : short
  {
    None = 0,

    [Description("When a data load fails")]
    DataLoadError = 1,

    [Description("When a data load completes")]
    DataLoadComplete = 2,

    [Description("When a rule run fails")]
    RuleRunError = 3,

    [Description("When a rule fails validation")]
    RuleRunValidationError = 4,

    [Description("When a rule run completes")]
    RuleRunComplete = 5,

    [Description("When a rule run completes and has breaches")]
    RuleRunCompleteWithBreaches = 6,

    [Description("When a breach has been assigned to me")]
    BreachAssigned

  }
}
