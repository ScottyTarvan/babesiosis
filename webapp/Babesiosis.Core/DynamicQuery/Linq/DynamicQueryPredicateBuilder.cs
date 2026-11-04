using Newtonsoft.Json.Linq;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Linq.Expressions;
using System.Reflection;

namespace Babesiosis.Core.DynamicQuery.Linq
{
  /// <summary>
  /// Builds the LINQ predicate for a list request's filter (platform/list-queries.md §3.1,
  /// §3.2, §3.5–§3.7), so Entity Framework can translate it to SQL.
  /// <para>
  /// <b>Grammar.</b> <c>[field, op, value]</c>; <c>['!', expr]</c>; groups joined by
  /// <c>and</c> / <c>or</c>, where AND groups before OR. Conditions side by side with no joiner,
  /// and the upper-case joiners <c>AND</c> / <c>OR</c>, combine the same way (§3.6). A top-level
  /// group whose joiner is any other word is not read and applies no filter (PL-56); the same
  /// shape anywhere else is an error.
  /// </para>
  /// <para>
  /// <b>Shape.</b> The expressions match the ones the list helpers produced before this builder
  /// replaced the DevExpress criteria path, so the generated SQL is unchanged: numeric operands
  /// are promoted to the wider type, a nullable field compares against a nullable constant, a
  /// text operator on a non-text field searches the field's text, and <c>= null</c> on a
  /// non-nullable field is simply false.
  /// </para>
  /// <para>
  /// A value is never concatenated into anything: it is a constant in the expression tree, which
  /// Entity Framework writes as an escaped SQL literal (a converted or <c>ToString()</c>-wrapped
  /// constant becomes a parameter). Field names only ever resolve to public properties.
  /// </para>
  /// </summary>
  public static class DynamicQueryPredicateBuilder
  {
    private const int MaxDepth = 64;

    private static readonly Dictionary<string, ExpressionType> Comparisons = new()
    {
      ["="] = ExpressionType.Equal,
      ["<>"] = ExpressionType.NotEqual,
      [">"] = ExpressionType.GreaterThan,
      ["<"] = ExpressionType.LessThan,
      [">="] = ExpressionType.GreaterThanOrEqual,
      ["<="] = ExpressionType.LessThanOrEqual,
    };

    private static readonly Dictionary<string, MethodInfo> TextOperators = new()
    {
      ["contains"] = typeof(string).GetMethod(nameof(string.Contains), new[] { typeof(string) }),
      ["notcontains"] = typeof(string).GetMethod(nameof(string.Contains), new[] { typeof(string) }),
      ["startswith"] = typeof(string).GetMethod(nameof(string.StartsWith), new[] { typeof(string) }),
      ["endswith"] = typeof(string).GetMethod(nameof(string.EndsWith), new[] { typeof(string) }),
    };

    private static readonly MethodInfo StringCompare =
      typeof(string).GetMethod(nameof(string.Compare), new[] { typeof(string), typeof(string) });

    private static readonly HashSet<string> Joiners = new() { "and", "or", "AND", "OR" };

    /// <summary>The predicate for <paramref name="filter"/>, or <c>null</c> when it applies no filter.</summary>
    public static Expression<Func<T, bool>> Build<T>(IList filter) =>
      (Expression<Func<T, bool>>)Build(typeof(T), filter);

    /// <inheritdoc cref="Build{T}(IList)"/>
    public static LambdaExpression Build(Type elementType, IList filter)
    {
      if (filter == null || filter.Count == 0) return null;

      var parameter = Expression.Parameter(elementType, "Param_0");
      var body = Node(parameter, Parts(filter), depth: 0, topLevel: true);

      return body == null ? null : Expression.Lambda(body, parameter);
    }

    private static Expression Node(ParameterExpression parameter, object[] parts, int depth, bool topLevel)
    {
      if (depth > MaxDepth)
        throw new NotSupportedException($"The filter is nested more than {MaxDepth} levels deep.");

      if (parts.Length == 0)
        throw new NotSupportedException("A filter group is empty.");

      if (parts[0] is string head)
      {
        if (head != "!") return Condition(parameter, parts);

        var negated = parts.Length > 1 ? AsList(parts[1]) : null;
        if (negated == null) throw new NotSupportedException("'!' must be followed by a condition or a group.");

        return Expression.Not(Node(parameter, Parts(negated), depth + 1, topLevel: false));
      }

      if (AsList(parts[0]) == null || parts.Length == 1)
        throw new NotSupportedException("A filter group needs at least two parts.");

      if (parts[1] is string joiner && !Joiners.Contains(joiner))
      {
        if (topLevel) return null;
        throw new NotSupportedException($"Unknown filter joiner '{joiner}'.");
      }

      return Group(parameter, parts, depth);
    }

    /// <summary>Operands combine with AND unless an 'or' separates them; OR binds loosest.</summary>
    private static Expression Group(ParameterExpression parameter, object[] parts, int depth)
    {
      var orTerms = new List<Expression>();
      Expression andChain = null;
      var pendingOr = false;
      var expectOperand = true;

      foreach (var part in parts)
      {
        if (part is string word)
        {
          if (!Joiners.Contains(word)) throw new NotSupportedException($"Unknown filter joiner '{word}'.");
          if (expectOperand) throw new NotSupportedException($"The joiner '{word}' has no condition before it.");

          pendingOr = string.Equals(word, "or", StringComparison.OrdinalIgnoreCase);
          expectOperand = true;
          continue;
        }

        var list = AsList(part) ?? throw new NotSupportedException("A filter group may only hold conditions, groups and joiners.");
        var operand = Node(parameter, Parts(list), depth + 1, topLevel: false);

        if (andChain == null)
        {
          andChain = operand;
        }
        else if (pendingOr)
        {
          orTerms.Add(andChain);
          andChain = operand;
        }
        else
        {
          andChain = Expression.AndAlso(andChain, operand);
        }

        pendingOr = false;
        expectOperand = false;
      }

      if (expectOperand) throw new NotSupportedException("A filter group ends with a joiner.");

      orTerms.Add(andChain);
      return orTerms.Aggregate(Expression.OrElse);
    }

    private static Expression Condition(ParameterExpression parameter, object[] parts)
    {
      if (parts.Length < 3)
        throw new NotSupportedException("A filter condition needs a field, an operator and a value.");

      var field = Convert.ToString(parts[0], CultureInfo.InvariantCulture);
      var op = (Convert.ToString(parts[1], CultureInfo.InvariantCulture) ?? string.Empty).Trim();
      var value = parts[2];

      if (TextOperators.TryGetValue(op, out var method))
      {
        var member = DynamicQueryMember.Resolve(parameter, field);
        var search = Text(member, method, value);
        return op == "notcontains" ? Expression.Not(search) : search;
      }

      if (Comparisons.TryGetValue(op, out var kind))
      {
        var literal = DynamicQueryLiteral.From(value);
        return Compare(DynamicQueryMember.Resolve(parameter, field), kind, literal);
      }

      throw new NotImplementedException("Unsupported operator: " + op);
    }

    private static Expression Text(Expression member, MethodInfo method, object value)
    {
      if (member.Type == typeof(string))
        return Expression.Call(member, method, SearchArgument(DynamicQueryLiteral.ForTextSearch(value)));

      var literal = DynamicQueryLiteral.From(value);
      var underlying = Nullable.GetUnderlyingType(member.Type);
      if (underlying == null)
        return Expression.Call(ToText(member), method, SearchArgument(literal));

      var search = Expression.Call(ToText(Expression.Convert(member, underlying)), method, SearchArgument(literal));

      return Expression.Condition(
        Expression.Equal(member, Expression.Constant(null, member.Type)),
        Expression.Constant(false),
        Expression.Convert(search, typeof(bool)));
    }

    private static Expression Compare(Expression member, ExpressionType kind, object literal)
    {
      var underlying = Nullable.GetUnderlyingType(member.Type);
      var nullable = underlying != null;
      underlying ??= member.Type;

      if (literal == null)
      {
        if (member.Type.IsValueType && !nullable)
        {
          if (kind == ExpressionType.Equal) return Expression.Constant(false);
          if (kind == ExpressionType.NotEqual) return Expression.Constant(true);

          var lifted = typeof(Nullable<>).MakeGenericType(member.Type);
          return Expression.MakeBinary(kind, Expression.Convert(member, lifted), Expression.Constant(null, lifted));
        }

        if (nullable && underlying.IsEnum)
          return Expression.MakeBinary(kind, Expression.Convert(member, typeof(int?)), Expression.Convert(Expression.Constant(null), typeof(int?)));

        if (member.Type == typeof(string) && IsOrdering(kind))
          return Expression.MakeBinary(kind, Expression.Call(StringCompare, member, Expression.Constant(null, typeof(string))), Expression.Constant(0));

        return Expression.MakeBinary(kind, member, Expression.Constant(null, member.Type));
      }

      if (underlying == typeof(string))
      {
        if (literal is not string text) throw Mismatch(kind, member.Type, literal);

        return IsOrdering(kind)
          ? Expression.MakeBinary(kind, Expression.Call(StringCompare, member, Expression.Constant(text)), Expression.Constant(0))
          : Expression.MakeBinary(kind, member, Expression.Constant(text));
      }

      // Before the numeric check: Type.GetTypeCode reports an enum as its underlying integer.
      if (underlying.IsEnum)
        return Enumeration(member, underlying, nullable, kind, literal);

      if (IsNumeric(underlying))
      {
        if (!IsNumeric(literal.GetType())) throw Mismatch(kind, member.Type, literal);
        return Numeric(member, underlying, nullable, kind, literal);
      }

      if (underlying == typeof(bool))
      {
        var flag = literal switch
        {
          bool value => value,
          string text when bool.TryParse(text, out var parsed) => parsed,
          _ => throw Mismatch(kind, member.Type, literal),
        };
        return Expression.MakeBinary(kind, member, Typed(flag, nullable, underlying));
      }

      if (underlying == typeof(Guid))
      {
        if (literal is string text && Guid.TryParse(text, out var key) && !IsOrdering(kind))
          return Expression.MakeBinary(kind, member, Typed(key, nullable, underlying));
        throw Mismatch(kind, member.Type, literal);
      }

      // A date literal always arrives as a DateTime; a calendar-date field compares its date part.
      if (underlying == typeof(DateOnly))
      {
        if (literal is not DateTime moment) throw Mismatch(kind, member.Type, literal);
        return Expression.MakeBinary(kind, member, Typed(DateOnly.FromDateTime(moment), nullable, underlying));
      }

      if (literal.GetType() == underlying)
        return Expression.MakeBinary(kind, member, Typed(literal, nullable, underlying));

      throw Mismatch(kind, member.Type, literal);
    }

    /// <summary>The wider of the two numeric types wins; a nullable field compares nullable.</summary>
    private static Expression Numeric(Expression member, Type underlying, bool nullable, ExpressionType kind, object literal)
    {
      var literalType = literal.GetType();
      var target = Rank(literalType) > Rank(underlying) ? literalType : underlying;
      var targetType = nullable ? typeof(Nullable<>).MakeGenericType(target) : target;

      Expression left = underlying == target ? member : Expression.Convert(member, targetType);
      Expression right = Expression.Constant(literal, literalType);

      if (nullable || literalType != target) right = Expression.Convert(right, targetType);

      return Expression.MakeBinary(kind, left, right);
    }

    /// <summary>
    /// An enum compares as its number, given either as a number or as a member name. A nullable
    /// enum compares as a nullable number, the literal passing through the enum type first.
    /// </summary>
    private static Expression Enumeration(Expression member, Type enumType, bool nullable, ExpressionType kind, object literal)
    {
      if (nullable)
      {
        Expression value = literal switch
        {
          int or long => Expression.Convert(Expression.Convert(Expression.Constant(literal), enumType), member.Type),
          string name when Enum.TryParse(enumType, name, ignoreCase: true, out var parsed) && Enum.IsDefined(enumType, parsed)
            => Expression.Convert(Expression.Constant(parsed, enumType), member.Type),
          _ => throw Mismatch(kind, member.Type, literal),
        };

        return Expression.MakeBinary(kind, Expression.Convert(member, typeof(int?)), Expression.Convert(value, typeof(int?)));
      }

      Type numberType;
      Expression right;

      switch (literal)
      {
        case int number:
          numberType = typeof(int);
          right = Expression.Constant(number);
          break;
        case long number:
          numberType = typeof(long);
          right = Expression.Constant(number);
          break;
        case string name when Enum.TryParse(enumType, name, ignoreCase: true, out var parsed) && Enum.IsDefined(enumType, parsed):
          numberType = typeof(int);
          right = Expression.Convert(Expression.Constant(parsed, enumType), typeof(int));
          break;
        default:
          throw Mismatch(kind, member.Type, literal);
      }

      return Expression.MakeBinary(kind, Expression.Convert(member, numberType), right);
    }

    private static Expression Typed(object value, bool nullable, Type type)
    {
      Expression constant = Expression.Constant(value, type);
      return nullable ? Expression.Convert(constant, typeof(Nullable<>).MakeGenericType(type)) : constant;
    }

    /// <summary>
    /// Text is searched as-is; any other literal searches for its text. A missing value is kept
    /// as a null search argument, exactly as before (it fails when the query runs).
    /// </summary>
    private static Expression SearchArgument(object value) => value switch
    {
      null => Expression.Constant(null, typeof(string)),
      string text => Expression.Constant(text),
      _ => Expression.Call(Expression.Constant(value), value.GetType().GetMethod(nameof(ToString), Type.EmptyTypes)),
    };

    private static Expression ToText(Expression value) =>
      Expression.Call(value, value.Type.GetMethod(nameof(ToString), Type.EmptyTypes));

    private static bool IsOrdering(ExpressionType kind) =>
      kind is not (ExpressionType.Equal or ExpressionType.NotEqual);

    private static bool IsNumeric(Type type) => Rank(type) >= 0;

    private static double Rank(Type type) => Type.GetTypeCode(type) switch
    {
      TypeCode.SByte or TypeCode.Byte or TypeCode.Int16 or TypeCode.UInt16 => 0,
      TypeCode.Int32 => 1,
      TypeCode.UInt32 => 1.5,
      TypeCode.Int64 => 2,
      TypeCode.UInt64 => 2.5,
      TypeCode.Decimal => 3,
      TypeCode.Single => 3.5,
      TypeCode.Double => 4,
      _ => -1,
    };

    private static Exception Mismatch(ExpressionType kind, Type fieldType, object literal) =>
      new InvalidOperationException(
        $"The binary operator {kind} is not defined for the types '{fieldType}' and '{literal.GetType()}'.");

    private static IList AsList(object value) => value switch
    {
      JArray array => array,
      string => null,
      IList list => list,
      _ => null,
    };

    private static object[] Parts(IList list) =>
      list.Cast<object>().Select(DynamicQueryLiteral.Unwrap).ToArray();
  }
}
