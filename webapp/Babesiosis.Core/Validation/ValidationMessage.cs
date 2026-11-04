using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Validation
{
  public class ValidationMessage
  {
    public static ValidationMessage Passed(string message, int code = 0)
    {
      return new ValidationMessage(message, code, ValidationMessageStatus.Passed);
    }

    public static ValidationMessage Warning(string message, int code = 0)
    {
      return new ValidationMessage(message, code, ValidationMessageStatus.Warning);
    }

    public static ValidationMessage Failed(string message, int code = 0)
    {
      return new ValidationMessage(message, code, ValidationMessageStatus.Failed);
    }

    public ValidationMessage(string message, int code = 0, ValidationMessageStatus status = ValidationMessageStatus.Failed)
    {
      Message = message;
      Code = code;
      Status = status;
    }

    public string Message { get; set; }
    public int Code { get; set; }
    public ValidationMessageStatus Status { get; set; }
    
  }
}
