using Babesiosis.Core.Models.Domain;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface IBlobStorageService
  {
    Task Connect(string connectionString = null);
    Task<List<BlobContainerModel>> GetContainersAsync(string connectionString = null);
    Task<List<BlobModel>> GetBlobsAsync(string containerName, string prefix = "", string connectionString = "");
    Task<BlobModel> GetBlobAsync(string containerName, string blobName, string connectionString = "");
    Task<bool> BlobExistsAsync(string containerName, string blobName, string connectionString = "");
    Task<string> GetBlobBase64Async(string containerName, string blobName, string connectionString = "");
    Task<Stream> DownloadBlobAsync(string containerName, string blobName, string connectionString = "");
    Task<(Stream Content, string ETag)> DownloadBlobWithETagAsync(string containerName, string blobName, string connectionString = "");
    string GetBlobDownloadLink(string containerName, string blobName, string filename, bool expires = true, string connectionString = "");
    Task<string> GetBlobDownloadLinkForManagedIdentityAsync(string containerName, string blobName, string filename, bool expires = true, string connectionString = "");
    bool CanGenerateDownloadLinks(string containerName, string connectionString = "");
    string GetBlobUrl(string containerName, string blobName, string connectionString = "");
    Task<BlobModel> AddBlobAsync(string containerName, Stream stream, string fileType = "application/octet-stream", string connectionString = "");
    Task<BlobModel> AddBlobAsync(string containerName, string blobName, Stream stream, string fileType = "application/octet-stream", string connectionString = "");
    Task<List<BlobModel>> AddBlobsAsync(string containerName, IEnumerable<BlobStream> streams, string contentType = BlobContentType.Octet, string connectionString = "");
    Task<BlobModel> UpdateBlobAsync(string containerName, string blobName, Stream stream, string fileType = BlobContentType.Octet, string connectionString = "");

    /// <summary>
    /// Writes the blob only if it still matches the caller's last-known state,
    /// using the storage provider's optimistic-concurrency (ETag) support.
    /// <paramref name="expectedETag"/> null means "the blob must not currently
    /// exist" (a create-only write); a non-null value means "the blob must
    /// still have exactly this ETag". Returns a failed result — rather than
    /// throwing — when a concurrent writer changed the blob first, so a
    /// racing reload can detect it lost the race and reload instead of
    /// silently overwriting newer data with stale data.
    /// </summary>
    Task<BlobConditionalWriteResult> UpdateBlobIfUnchangedAsync(string containerName, string blobName, Stream stream, string expectedETag, string fileType = BlobContentType.Octet, string connectionString = "");

    Task<bool> DeleteBlobAsync(string containerName, string blobName, string connectionString = "");
    Task ClearContainerAsync(string containerName, string connectionString = "");
    Task DeleteFolderAsync(string containerName, string folderPath, string connectionString = "");
    Task<long> GetBlobSizeAsync(string containerName, string blobName, string connectionString = "");
    Task<string> GetBlobETagAsync(string containerName, string blobName, string connectionString = "");

  }
}
