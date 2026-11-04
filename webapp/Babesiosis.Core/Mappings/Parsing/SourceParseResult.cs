using System.Collections.Generic;
using System.Linq;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// Everything one parse produced: the field list that becomes <c>source_field</c> rows, and the
  /// preview rows that do not.
  ///
  /// <para>
  /// The asymmetry is the point. <see cref="Fields"/> is persisted; <see cref="SampleRows"/> is
  /// returned to the browser so the analyst can confirm the parse settings and is then discarded,
  /// because PRD §9 puts movement or persistence of source data rows out of scope. The only source
  /// data that survives the request is one <see cref="ParsedField.SampleValue"/> per field.
  /// </para>
  /// </summary>
  public class SourceParseResult
  {
    /// <summary>The fields, in file order, ordinals 1..N. Never null; never empty on a successful parse.</summary>
    public IReadOnlyList<ParsedField> Fields { get; set; } = new List<ParsedField>();

    /// <summary>
    /// Up to <see cref="SourceParseOptions.MaxSampleRows"/> data rows, every one padded or truncated
    /// to <see cref="Fields"/> width so the preview is rectangular even when the file is not.
    /// Empty when the file has a header and no data — PRD §6 says that is not an error.
    /// </summary>
    public IReadOnlyList<string[]> SampleRows { get; set; } = new List<string[]>();

    /// <summary>
    /// For Excel, every worksheet in the workbook, so the UI can render the sheet picker from the
    /// first parse instead of asking the analyst to guess a name and re-upload. Empty for the text
    /// formats, which have no such concept.
    /// </summary>
    public IReadOnlyList<string> SheetNames { get; set; } = new List<string>();

    /// <summary>
    /// The single place a parse result is assembled, shared by all three parsers.
    ///
    /// <para>
    /// Centralising it is what makes the format-independent rules actually format-independent: name
    /// disambiguation, padding the preview to the header width, capping the sample, picking one
    /// sample value per field and inferring a type all happen here exactly once. A per-parser copy
    /// of this would drift, and the drift would only show up as an Excel file behaving unlike a CSV
    /// with the same columns.
    /// </para>
    ///
    /// <para>
    /// <paramref name="dataRows"/> is enumerated lazily and abandoned as soon as the sample is full,
    /// so a 5 MB file is not materialised to hand back ten rows.
    /// </para>
    /// </summary>
    /// <param name="rawHeaderNames">
    /// Header cells as they appeared, or a run of nulls when there is no header row — the null run
    /// is what produces <c>COLUMN_1 … COLUMN_N</c>. Its length fixes the field count: PRD §6 requires
    /// field extraction to be driven by the header row alone, so a ragged data row can neither add
    /// nor remove a field.
    /// </param>
    /// <param name="dataRows">The rows below the header, in file order, raggedness and all.</param>
    /// <param name="maxSampleRows">Ceiling on preview rows. Values below zero are treated as zero.</param>
    /// <param name="sheetNames">Workbook sheet names, or null for the text formats.</param>
    public static SourceParseResult Build(IReadOnlyList<string> rawHeaderNames,
      IEnumerable<string[]> dataRows, int maxSampleRows, IReadOnlyList<string> sheetNames = null)
    {
      var names = ParsedField.Disambiguate(rawHeaderNames);
      var width = names.Count;
      var cap = maxSampleRows < 0 ? 0 : maxSampleRows;

      var samples = new List<string[]>();
      if (cap > 0 && dataRows != null)
      {
        foreach (var row in dataRows)
        {
          if (samples.Count >= cap)
          {
            break;
          }

          // Pad or truncate to the header width. Both directions matter: a short row must not throw
          // when the preview reads column 5, and a long row must not push a value into a column the
          // analyst cannot bind because it has no field.
          var rectangular = new string[width];
          for (var i = 0; i < width; i++)
          {
            rectangular[i] = row != null && i < row.Length && row[i] != null ? row[i] : string.Empty;
          }

          samples.Add(rectangular);
        }
      }

      var fields = new List<ParsedField>(width);
      for (var i = 0; i < width; i++)
      {
        var column = samples.Select(r => r[i]).ToList();

        fields.Add(new ParsedField
        {
          Name = names[i],
          Ordinal = i + 1,
          SampleValue = column.FirstOrDefault(v => !string.IsNullOrWhiteSpace(v)),
          InferredType = SourceTypeInference.Infer(column)
        });
      }

      return new SourceParseResult
      {
        Fields = fields,
        SampleRows = samples,
        SheetNames = sheetNames ?? new List<string>()
      };
    }
  }
}
