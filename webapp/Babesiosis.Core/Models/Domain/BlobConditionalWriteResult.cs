namespace Babesiosis.Core.Models.Domain
{

  /// <summary>
  /// The outcome of an optimistic-concurrency blob write (see
  /// <see cref="Babesiosis.Core.Services.IBlobStorageService.UpdateBlobIfUnchangedAsync"/>).
  /// A failed precondition is reported here rather than thrown, since a caller
  /// racing another writer treats it as an expected outcome to react to, not
  /// an error to log.
  /// </summary>
  public class BlobConditionalWriteResult
  {
    /// <summary>
    /// True when the write happened because the blob still matched the
    /// caller's expectation. False when a concurrent writer changed the blob
    /// first — its precondition failed and nothing was written.
    /// </summary>
    public bool Success { get; set; }

    /// <summary>The written blob's new state. Null when <see cref="Success"/> is false.</summary>
    public BlobModel Blob { get; set; }
  }
}
