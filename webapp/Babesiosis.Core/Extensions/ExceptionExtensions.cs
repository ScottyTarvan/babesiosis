using System;
using System.Collections.Generic;
using System.Globalization;
using System.Text.RegularExpressions;

namespace Babesiosis.Core.Extensions
{
  public static class ExceptionExtensions
  {
    public static Exception Unwrap(this Exception ex)
    {
      string result = ex.Message;

      while (ex.InnerException != null)
      {
        result = result + ", " + ex.InnerException.ToString();
        ex = ex.InnerException;
      }

      return new Exception(result);
    }
  }
}
