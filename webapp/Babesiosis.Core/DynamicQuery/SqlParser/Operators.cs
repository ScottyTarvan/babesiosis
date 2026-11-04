namespace Babesiosis.Core.DynamicQuery.SqlParser
{
  internal static class Operators
  {
    public static string CONTAINS = "contains";
    public static string STARTS_WITH = "startswith";
    public static string ENDS_WITH = "endswith";
    public static string BETWEEN = "between";
    public static string NOT_EQUALS = "<>";
    public static string EQUALS = "=";
    public static string GREATER = ">";
    public static string LESS = "<";
    public static string AND = "and";
    public static string OR = "or";
    public static string IS = "is";

    public static string[] OPERATORS = { CONTAINS, STARTS_WITH, ENDS_WITH, BETWEEN, NOT_EQUALS, EQUALS, GREATER, LESS, IS };
    public static string[] LOGIC_OPERATORS = { AND, OR };
  }
}
