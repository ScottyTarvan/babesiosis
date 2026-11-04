using Babesiosis.Core.Exceptions;
using Babesiosis.Core.Extensions;
using System;
using System.Collections;
using System.Security;

namespace Babesiosis.Core.Assertions
{
  public static class Assertion
  {
    public static void Throw(string message)
    {
      throw new ValidationException(message);
    }

    public static void Authenticate(object item, string message)
    {
      if (item == null)
      {
        throw new SecurityException(message);
      }
    }

    /// <summary>
    /// Refuses a null. Throws <see cref="ValidationException"/>, not
    /// <see cref="NullReferenceException"/>: almost every call site is a lookup whose message
    /// ("X does not exist for id …") is written for the caller, and the function apps turn a
    /// ValidationException into a 400 carrying that message, where any other exception becomes a
    /// 500 with a generic one.
    /// </summary>
    public static void IsNotNull(object item, string name, string message = null)
    {
      if (item == null)
      {
        throw new ValidationException(message ?? $"{name} is null");
      }
    }

    public static void IsNotNull(object item, string message)
    {
      IsNotNull(item, "", message);
    }

    public static void IsNull(object item, string name, string message = null)
    {
      if (item != null)
      {
        throw new NullReferenceException(message ?? $"{name} is not null");
      }
    }

    public static void IsNull(object item, string message)
    {
      IsNull(item, "", message);
    }

    public static void IsNotEmptyString(string item, string name, string message = null)
    {
      if (String.IsNullOrEmpty(item))
      {
        throw new Exception(message ?? $"{name} has no value");
      }
    }

    public static void IsNotEmptyString(string item, string message)
    {
      IsNotEmptyString(item, "", message);
    }

    public static void AreEqual(object x, object y, string message)
    {
      IsNotNull(x, "Item1");
      IsNotNull(y, "Item1");

      if (!x.Equals(y))
      {
        throw new ValidationException(message);
      }
    }

    public static void AreNotEqual(object x, object y, string message)
    {
      IsNotNull(x, "Item1");
      IsNotNull(y, "Item1");

      if (x.Equals(y))
      {
        throw new ValidationException(message);
      }
    }

    public static void HasItems(IEnumerable items, string message)
    {
      if (!items.Any())
      {
        throw new ValidationException(message);
      }
    }

    public static void HasNoItems(IEnumerable items, string messsage)
    {
      if (items.Any())
      {
        throw new ValidationException(messsage);
      }
    }

    public static void Invalid(string message)
    {
      throw new ValidationException(message);
    }

    public static void True(bool value, string message)
    {
      if (!value)
      {
        throw new ValidationException(message);
      }
    }

    public static void False(bool value, string message)
    {
      if (value)
      {
        throw new ValidationException(message);
      }
    }

    public static void RowVersionCheck(byte[] myVersion, string theirVersion, string message)
    {
      if (myVersion.ToBase64String() != theirVersion)
      {
        throw new ConcurrencyException(message);
      }
    }
  }
}
