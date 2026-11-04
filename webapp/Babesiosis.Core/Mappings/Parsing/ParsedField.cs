using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// One field discovered in a source file — the parser's shape of PRD §4 <c>source_field</c>.
  ///
  /// <para>
  /// Note what is *not* here: no id, no mapping reference, no persistence concern. The parser knows
  /// nothing about which mapping asked for the parse, which is what lets the same instance be
  /// produced by a unit test with a <c>MemoryStream</c> and by the upload endpoint.
  /// </para>
  /// </summary>
  public class ParsedField
  {
    /// <summary>
    /// U+FEFF, the byte-order mark. Written as a numeric cast rather than as the character itself so
    /// it stays visible to anyone reading this file — a literal BOM in source is precisely the
    /// invisible character this code exists to remove.
    /// </summary>
    internal const char BomCharacter = (char)0xFEFF;

    /// <summary>
    /// The field name after trimming, blank substitution and duplicate disambiguation. Unique within
    /// a result, case-insensitively, because <c>source_field</c> carries
    /// <c>UNIQUE (mapping_id, name)</c> under a case-insensitive collation.
    /// </summary>
    public string Name { get; set; }

    /// <summary>1-based position in the file, matching <c>source_field.ordinal</c>.</summary>
    public int Ordinal { get; set; }

    /// <summary>
    /// <c>STRING|INTEGER|DECIMAL|DATE|BOOLEAN</c>, guessed from the sample rows.
    /// TODO(spec) Q2: advisory only — nothing gates on it, and a wrong guess costs the analyst an
    /// icon, never a saved binding.
    /// </summary>
    public string InferredType { get; set; }

    /// <summary>
    /// The first non-blank value seen for this field in the sample rows, or null when every sampled
    /// row was blank. PRD §2 Story 2 caps persistence of source *data* at exactly this one value per
    /// field — the sample rows themselves are returned for preview and thrown away.
    /// </summary>
    public string SampleValue { get; set; }

    /// <summary>
    /// Turns raw header cells into the final field names, applying the four PRD §2 Story 2 rules in
    /// one place so delimited, Excel and fixed-width cannot drift apart: trim; a blank cell becomes
    /// <c>COLUMN_{ordinal}</c>; a byte-order mark left on the first cell is stripped; duplicates get
    /// <c>_2</c>, <c>_3</c>.
    ///
    /// <para>
    /// The collision set is case-insensitive on purpose. The database's unique index sits under a
    /// case-insensitive collation, so letting <c>Amount</c> and <c>AMOUNT</c> both through here
    /// would trade a clean rename for a constraint violation on save.
    /// </para>
    ///
    /// <para>
    /// The suffix loop re-tests each candidate rather than assuming <c>_2</c> is free, because a file
    /// is allowed to contain a literal column called <c>AMOUNT_2</c> alongside two called
    /// <c>AMOUNT</c>; the second <c>AMOUNT</c> then has to land on <c>AMOUNT_3</c>.
    /// </para>
    /// </summary>
    public static IReadOnlyList<string> Disambiguate(IEnumerable<string> rawNames)
    {
      var names = new List<string>();
      var used = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
      var ordinal = 0;

      foreach (var raw in rawNames)
      {
        ordinal++;

        // The BOM is stripped from the decoded text as well; this is the second line of defence,
        // because a BOM surviving into the first field name is an explicit PRD §6 failure.
        var name = (raw ?? string.Empty).TrimStart(BomCharacter).Trim();
        if (name.Length == 0)
        {
          name = "COLUMN_" + ordinal;
        }

        var candidate = name;
        var suffix = 1;
        while (!used.Add(candidate))
        {
          suffix++;
          candidate = name + "_" + suffix;
        }

        names.Add(candidate);
      }

      return names;
    }
  }
}
