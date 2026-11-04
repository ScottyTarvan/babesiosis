using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;

namespace Babesiosis.Core.Security
{
  public class PasswordPolicy
  {
    private readonly string _password;

    private readonly IDictionary<string, Func<string, bool>> _rules;

    public PasswordPolicy(string password)
    {
      _password = password;
      _rules = new Dictionary<string, Func<string, bool>>
      {
        { "Password must contain at least 8 characters", CheckLength },
        { "Password must contain at least 1 numeric character", CheckNumericCharacters },
        { "Password must contain at least 1 symbol", CheckSymbolCharacters },
        { "Password must contain at least 1 uppercase alpha character", CheckUppercaseAlpha },
        { "Password must contain at least 1 lowercase alpha character", CheckLowercaseAlpha },
      };
    }

    public PasswordPolicyResult Validate()
    {
      var failedRules = _rules.Select(r => r.Value(_password) ? null : r.Key).Where(msg => !string.IsNullOrEmpty(msg));
      return new PasswordPolicyResult
      {
        Valid = failedRules.Count() == 0,
        Errors = failedRules
      };
    }

    public class PasswordPolicyResult
    {
      public bool Valid { get; set; }
      public IEnumerable<string> Errors { get; set; }
    }

    private bool CheckLength(string val) => val.Length >= 8;

    private bool CheckNumericCharacters(string val) => new Regex("[0-9]").IsMatch(val);

    private bool CheckSymbolCharacters(string val) => val.Any(c => !char.IsLetterOrDigit(c));

    private bool CheckUppercaseAlpha(string val) => new Regex("[A-Z]").IsMatch(val);

    private bool CheckLowercaseAlpha(string val) => new Regex("[a-z]").IsMatch(val);
  }
}
