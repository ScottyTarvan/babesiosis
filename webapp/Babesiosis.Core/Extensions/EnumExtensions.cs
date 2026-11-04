using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using Babesiosis.Core.Annotations;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Extensions
{
  public static class EnumExtensions
  {
    /// <summary>
    /// Parse a string value and convert to an enum
    /// </summary>
    /// <typeparam name="T"></typeparam>
    /// <param name="enum"></param>
    /// <returns></returns>
    public static T ParseEnum<T>(this string @enum)
    {
      return (T)Enum.Parse(typeof(T), @enum);
    }

    /// <summary>
    /// Get a description attribute from an enum
    /// </summary>
    /// <typeparam name="TAttribute"></typeparam>
    /// <param name="enum"></param>
    /// <returns></returns>
    public static string GetDescription(this Enum @enum)
    {
      var type = @enum.GetType();
      var name = Enum.GetName(type, @enum);

      var attribute = type.GetField(name)
          .GetCustomAttributes(false)
          .OfType<DescriptionAttribute>()
          .SingleOrDefault();

      return attribute != null ? attribute.Description : name;
    }

    /// <summary>
    /// Get a categoru attribute from an enum
    /// </summary>
    /// <typeparam name="TAttribute"></typeparam>
    /// <param name="enum"></param>
    /// <returns></returns>
    public static string GetCategory(this Enum @enum)
    {
      var type = @enum.GetType();
      var name = Enum.GetName(type, @enum);

      var attribute = type.GetField(name)
          .GetCustomAttributes(false)
          .OfType<CategoryAttribute>()
          .SingleOrDefault();

      return attribute != null ? attribute.Category : name;
    }


    /// <summary>
    /// Get a number attribute from an enum
    /// </summary>
    /// <typeparam name="TAttribute"></typeparam>
    /// <param name="enum"></param>
    /// <returns></returns>
    public static int GetNumber(this Enum @enum)
    {
      var type = @enum.GetType();
      var name = Enum.GetName(type, @enum);

      var attribute = type.GetField(name)
          .GetCustomAttributes(false)
          .OfType<NumberAttribute>()
          .SingleOrDefault();

      return attribute != null ? attribute.Number : 0;
    }

    /// <summary>
    /// Get a symbol attribute from an enum
    /// </summary>
    /// <typeparam name="TAttribute"></typeparam>
    /// <param name="enum"></param>
    /// <returns></returns>
    public static string GetSymbol(this Enum @enum)
    {
      var type = @enum.GetType();
      var name = Enum.GetName(type, @enum);

      var attribute = type.GetField(name)
          .GetCustomAttributes(false)
          .OfType<SymbolAttribute>()
          .SingleOrDefault();

      return attribute != null ? attribute.Symbol : String.Empty;
    }

    public static List<ListItemViewModel<TEnum>> ToListItems<TEnum>(this TEnum @enum,
        Func<TEnum, bool> filter = null)
        where TEnum : Enum
    {
      return Enum.GetValues(typeof(TEnum))
          .OfType<TEnum>()
          .Where(e => filter == null || filter(e))
          .Select(e => new ListItemViewModel<TEnum>(e))
          .OrderBy(item => item.Name)
          .ToList();
    }
  }
}
