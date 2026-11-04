using Babesiosis.Core.Assertions;
using System;

namespace Babesiosis.Core.Models.Domain
{
    public class CurrencyRate : IdModel
  {
   /// <summary>
   /// Converts one currency to another using both the from and to rates for a base currency
   /// </summary>
   /// <param name="amount"></param>
   /// <param name="fromRate"></param>
   /// <param name="toRate"></param>
   /// <returns></returns>
    public static decimal Convert(decimal amount, decimal fromRate, decimal toRate)
    {
      Assertion.AreNotEqual(0m, toRate, "To rate cannot be zero");
      return amount * (fromRate / toRate);
    }

    /// <summary>
    /// Converts two rates into a single rate for a currency conversion 
    /// </summary>
    /// <param name="fromRate"></param>
    /// <param name="toRate"></param>
    /// <returns></returns>
    public static decimal CalculateRate( decimal fromRate, decimal toRate)
    {
      Assertion.AreNotEqual(0m, toRate, "To rate cannot be zero");
      return fromRate / toRate;
    }

    public int FromCurrencyId { get; set; }
    public int ToCurrencyId { get; set; }
    public DateTime CreatedDate { get; set; }
    public decimal Rate { get; set; }
    public Currency FromCurrency { get; set; }
    public Currency ToCurrency { get; set; }
  }
}
