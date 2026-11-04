using System.Collections.Generic;

namespace Babesiosis.Core.Validation
{
  public class ValidationMessages : List<ValidationMessage>
  {
    public ValidationMessage Add(string message, int code = 0, ValidationMessageStatus status = ValidationMessageStatus.Failed)
    {
      ValidationMessage validationMessage = new ValidationMessage
        (
          message,
          code,
          status
        );

      this.Add(validationMessage);

      return validationMessage;
    }
  }
}
