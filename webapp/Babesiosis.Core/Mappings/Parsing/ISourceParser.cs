using System.IO;
using System.Threading;
using System.Threading.Tasks;

namespace Babesiosis.Core.Mappings.Parsing
{
  /// <summary>
  /// One source format, reduced to a pure function over a <see cref="Stream"/>.
  ///
  /// <para>
  /// The interface takes no dependencies and every implementation is constructible with <c>new</c>.
  /// That is deliberate and load-bearing: parsing is the highest-risk correctness surface in this
  /// feature, so it has to be exercisable from a unit test holding a <c>MemoryStream</c>, with no
  /// HTTP request, no DbContext, no container and no fixture files. The moment a parser needs
  /// injecting, the cheap exhaustive tests stop being cheap.
  /// </para>
  ///
  /// <para>
  /// Implementations must not close or dispose the stream — the caller owns it, and the upload
  /// endpoint reads the same buffer again to re-parse under changed options.
  /// </para>
  /// </summary>
  public interface ISourceParser
  {
    /// <summary>
    /// Reads the stream under <paramref name="options"/> and returns the fields plus preview rows.
    /// Throws <see cref="SourceParseException"/> — and only that — for anything the caller's file or
    /// options got wrong, so a controller can map <see cref="SourceParseException.Code"/> to the
    /// PRD §5 envelope without inspecting exception text.
    /// </summary>
    SourceParseResult Parse(Stream stream, SourceParseOptions options);

    /// <summary>
    /// The awaitable face of <see cref="Parse"/>, for callers on an async path.
    ///
    /// <para>
    /// Parsing is CPU-bound over an already-buffered ≤ 5 MB stream, so there is no I/O to await and
    /// no thread is freed by making this genuinely asynchronous. It completes synchronously by
    /// design: PRD §7 fixes parsing as synchronous within the request, and offloading it to the pool
    /// would buy latency, not throughput.
    /// </para>
    /// </summary>
    Task<SourceParseResult> ParseAsync(Stream stream, SourceParseOptions options,
      CancellationToken cancellationToken = default);
  }
}
