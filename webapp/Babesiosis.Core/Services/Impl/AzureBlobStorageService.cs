using Azure;
using Azure.Core;
using Azure.Identity;
using Azure.Storage;
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;
using Azure.Storage.Blobs.Specialized;
using Azure.Storage.Sas;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Domain;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Abstractions;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services.Impl
{
  internal class AzureBlobStorageService : IBlobStorageService
  {
    private readonly IAppSettings _appSettings;
    private readonly BlobStorageClientManager _clientManager;
    private readonly ILogger<AzureBlobStorageService> _logger;

    internal AzureBlobStorageService(
      IAppSettings appSettings,
      BlobStorageClientManager clientManager,
      ILogger<AzureBlobStorageService> logger)
    {
      _appSettings = appSettings ?? throw new ArgumentNullException(nameof(appSettings));
      _clientManager = clientManager ?? throw new ArgumentNullException(nameof(clientManager));
      _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task Connect(string connectionString = null)
    {
      try
      {
        _logger.LogInformation("Testing blob storage connection");
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, "yoda");
        var exists = await containerClient.ExistsAsync();
        _logger.LogInformation("Blob storage connection test successful");
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to connect to blob storage");
        throw;
      }
    }

    public async Task<List<BlobContainerModel>> GetContainersAsync(string connectionString = null)
    {
      try
      {
        _logger.LogInformation("Retrieving blob containers");
        var serviceClient = CreateServiceClient(connectionString);
        var page = serviceClient.GetBlobContainersAsync(BlobContainerTraits.Metadata);

        var result = new List<BlobContainerModel>();
        await foreach(var item in page)
        {
          result.Add
          (
           new BlobContainerModel()
            {
              Name = item.Name
            }
          );
        }

        _logger.LogInformation("Retrieved {Count} blob containers", result.Count);
        return result;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to retrieve blob containers");
        throw;
      }
    }

    public async Task<List<BlobModel>> GetBlobsAsync(string containerName,
      string prefix = "",
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Retrieving blobs from container {ContainerName} with prefix '{Prefix}'", containerName, prefix);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobs = new List<BlobModel>();

        await foreach (BlobHierarchyItem blobItem in containerClient.GetBlobsByHierarchyAsync(BlobTraits.None, BlobStates.None, "/", prefix, default))
        {
          var model = new BlobModel();
          model.IsPrefix = blobItem.IsPrefix;

          if (blobItem.IsPrefix)
          {
            string[] parts = blobItem.Prefix.Split('/', StringSplitOptions.RemoveEmptyEntries);
            model.Name = parts[^1];
            model.Prefix = blobItem.Prefix;
          }
          else
          {
            string[] parts = blobItem.Blob.Name.Split('/', StringSplitOptions.RemoveEmptyEntries);
            model.Name = parts[^1];
            model.Prefix = blobItem.Blob.Name;
            // Listing results carry the length already — no per-blob round trip.
            // Rounded up, so a non-empty file never reads as 0 KB.
            var bytes = blobItem.Blob.Properties?.ContentLength ?? 0;
            model.SizeKb = (bytes + 1023) / 1024;
          }

          blobs.Add(model);
        }

        _logger.LogInformation("Retrieved {Count} blobs from container {ContainerName}", blobs.Count, containerName);
        return blobs;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to retrieve blobs from container {ContainerName}", containerName);
        throw;
      }
    }

    public async Task<BlobModel> GetBlobAsync(string containerName,
      string blobName,
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Retrieving blob {BlobName} from container {ContainerName}", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var props = await blobClient.GetPropertiesAsync();
        var sizeKb = props.Value.ContentLength / 1024;

        _logger.LogInformation("Retrieved blob {BlobName}, Size: {SizeKB}KB", blobName, sizeKb);
        return new BlobModel()
        {
          Name = blobName,
          SizeKb = sizeKb,
          Link = blobClient.Uri.AbsoluteUri
        };
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to retrieve blob {BlobName} from container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<bool> BlobExistsAsync(string containerName,
      string blobName,
      string connectionString = "")
    {
      try
      {
        _logger.LogDebug("Checking existence of blob {BlobName} in container {ContainerName}", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var exists = await blobClient.ExistsAsync();
        return exists.Value;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to check existence of blob {BlobName} in container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<String> GetBlobBase64Async(string containerName,
      string blobName,
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Downloading blob {BlobName} from container {ContainerName} as Base64", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        // Optimized: Use BinaryData for single allocation instead of double memory usage
        var response = await blobClient.DownloadContentAsync();
        var base64 = Convert.ToBase64String(response.Value.Content.ToMemory().Span);

        _logger.LogInformation("Downloaded blob {BlobName} as Base64, Length: {Length} chars", blobName, base64.Length);
        return base64;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to download blob {BlobName} from container {ContainerName} as Base64", blobName, containerName);
        throw;
      }
    }

    public async Task<Stream> DownloadBlobAsync(string containerName,
      string blobName,
      string connectionString)
    {
      try
      {
        _logger.LogInformation("Downloading blob {BlobName} from container {ContainerName} as stream", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        // Fixed: Return SDK stream directly instead of creating MemoryStream
        // This prevents memory leak - SDK handles disposal
        var response = await blobClient.DownloadStreamingAsync();
        _logger.LogInformation("Downloaded blob {BlobName} as stream", blobName);
        return response.Value.Content;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to download blob {BlobName} from container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<(Stream Content, string ETag)> DownloadBlobWithETagAsync(string containerName,
      string blobName,
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Downloading blob {BlobName} from container {ContainerName} as stream", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var response = await blobClient.DownloadStreamingAsync();
        _logger.LogInformation("Downloaded blob {BlobName} as stream", blobName);
        return (response.Value.Content, response.Value.Details.ETag.ToString());
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to download blob {BlobName} from container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public string GetBlobDownloadLink(string containerName,
      string blobName,
      string filename = "file",
      bool expires = true,
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Generating SAS download link for blob {BlobName} in container {ContainerName}, Expires: {Expires}", blobName, containerName, expires);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        if (blobClient.CanGenerateSasUri)
        {
          var expirationHours = expires ? _appSettings.BlobStorage.DefaultSasExpirationHours : (_appSettings.BlobStorage.NonExpiringSasExpirationYears * 365 * 24);
          BlobSasBuilder blobSasBuilder = new BlobSasBuilder()
          {
            BlobContainerName = containerName,
            BlobName = blobName,
            Resource = "b",
            ContentDisposition = $"attachment; filename={filename}",
            StartsOn = DateTimeOffset.UtcNow.AddMinutes(-5),
            ExpiresOn = expires
              ? DateTimeOffset.UtcNow.AddHours(_appSettings.BlobStorage.DefaultSasExpirationHours)
              : DateTimeOffset.UtcNow.AddYears(_appSettings.BlobStorage.NonExpiringSasExpirationYears)
          };

          blobSasBuilder.SetPermissions(BlobSasPermissions.Read);

          string sas = blobClient.GenerateSasUri(blobSasBuilder).Query;
          string sasUrl = $"{blobClient.Uri}{sas}";

          _logger.LogInformation("Generated SAS download link for blob {BlobName}, Expiration: {ExpirationHours}h", blobName, expirationHours);
          return sasUrl;
        }

        _logger.LogWarning("Cannot generate SAS URI for blob {BlobName}, returning default", blobName);
        return "assets/media/avatars/blank.png";
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to generate SAS download link for blob {BlobName} in container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<string> GetBlobDownloadLinkForManagedIdentityAsync(string containerName,
      string blobName,
      string filename = "file",
      bool expires = true,
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Generating SAS download link for blob {BlobName} in container {ContainerName}, Expires: {Expires}", blobName, containerName, expires);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var startsOn = DateTimeOffset.UtcNow.AddMinutes(-5);
        var expiresOn = expires
          ? DateTimeOffset.UtcNow.AddHours(_appSettings.BlobStorage.DefaultSasExpirationHours)
          : DateTimeOffset.UtcNow.AddYears(_appSettings.BlobStorage.NonExpiringSasExpirationYears);

        BlobSasBuilder blobSasBuilder = new BlobSasBuilder()
        {
          BlobContainerName = GetContainerName(containerName),
          BlobName = blobClient.Name,
          Resource = "b",
          ContentDisposition = $"attachment; filename={filename}",
          StartsOn = startsOn,
          ExpiresOn = expiresOn
        };
        blobSasBuilder.SetPermissions(BlobSasPermissions.Read);

        if (blobClient.CanGenerateSasUri)
        {
          string sas = blobClient.GenerateSasUri(blobSasBuilder).Query;
          _logger.LogInformation("Generated shared-key SAS for blob {BlobName}", blobName);
          return $"{blobClient.Uri}{sas}";
        }

        // User delegation SAS (managed identity / DefaultAzureCredential).
        // Azure caps user delegation keys at 7 days, so a "non-expiring" link is impossible here -
        // asking for more makes GetUserDelegationKeyAsync fail outright.
        var maxExpiry = startsOn.Add(BlobStorageClientManager.MaxUserDelegationSasLifetime);
        if (blobSasBuilder.ExpiresOn > maxExpiry)
        {
          _logger.LogWarning(
            "Requested SAS expiry {RequestedExpiry} exceeds the 7 day user-delegation limit for blob {BlobName}; clamping to {ClampedExpiry}",
            blobSasBuilder.ExpiresOn, blobName, maxExpiry);
          blobSasBuilder.ExpiresOn = maxExpiry;
        }

        var userDelegationKey = await _clientManager.GetUserDelegationKeyAsync(serviceClient, startsOn, blobSasBuilder.ExpiresOn);
        var sasParams = blobSasBuilder.ToSasQueryParameters(userDelegationKey, serviceClient.AccountName);
        _logger.LogInformation("Generated user-delegation SAS for blob {BlobName}", blobName);
        return $"{blobClient.Uri}?{sasParams}";
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to generate SAS download link for blob {BlobName} in container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public bool CanGenerateDownloadLinks(string containerName, string connectionString = "")
    {
      var serviceClient = CreateServiceClient(connectionString);
      var containerClient = CreateContainerClient(serviceClient, containerName);
      return containerClient.CanGenerateSasUri;
    }

    public string GetBlobUrl(string containerName, string blobName, string connectionString = "")
    {
      try
      {
        _logger.LogDebug("Getting URL for blob {BlobName} in container {ContainerName}", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        return blobClient.Uri.AbsoluteUri;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to get URL for blob {BlobName} in container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<BlobModel> AddBlobAsync(string containerName,
      Stream stream,
      string contentType = BlobContentType.Octet,
      string connectionString = "")
    {
      string blobName = Guid.NewGuid().ToD();
      return await AddBlobAsync(containerName, blobName, stream, contentType, connectionString);
    }


    public async Task<List<BlobModel>> AddBlobsAsync(string containerName,
      IEnumerable<BlobStream> streams,
      string contentType = BlobContentType.Octet,
      string connectionString = "")
    {
      try
      {
        var streamsList = streams.ToList();
        _logger.LogInformation("Starting batch upload of {Count} blobs to container {ContainerName}", streamsList.Count, containerName);

        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);

        List<BlobModel> results = new();
        int processedCount = 0;

        foreach (BlobStream[] chunk in streamsList.Chunk(8))
        {
          var tasks = new Queue<Task<Response<BlobContentInfo>>>();
          List<(BlobClient, long?)> chunkBlobs = new();

          foreach (BlobStream blobStream in chunk)
          {
            BlobClient blob = containerClient.GetBlobClient(blobStream.Name);

            var headers = new BlobHttpHeaders();
            headers.ContentType = contentType;

            if(blobStream.Blob.CanSeek)
            {
              blobStream.Blob.Position = 0;
            }

            tasks.Enqueue(blob.UploadAsync(blobStream.Blob, headers));
            chunkBlobs.Add((blob, blobStream.Blob.Length));
          }

          await Task.WhenAll(tasks);
          results.AddRange(chunkBlobs.Select(c => new BlobModel(c.Item1.Name, c.Item1.Uri.AbsoluteUri, c.Item2)));

          processedCount += chunk.Length;
          _logger.LogDebug("Processed {ProcessedCount}/{TotalCount} blobs", processedCount, streamsList.Count);
        }

        _logger.LogInformation("Successfully uploaded {Count} blobs to container {ContainerName}", results.Count, containerName);
        return results;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to batch upload blobs to container {ContainerName}", containerName);
        throw;
      }
    }

    public async Task<BlobModel> AddBlobAsync(string containerName,
      string blobName,
      Stream stream,
      string contentType = BlobContentType.Octet,
      string connectionString = "")
    {
      try
      {
        var sizeKb = stream.Length / 1024;
        _logger.LogInformation("Uploading blob {BlobName} to container {ContainerName}, Size: {SizeKB}KB, ContentType: {ContentType}",
          blobName, containerName, sizeKb, contentType);

        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var headers = new BlobHttpHeaders();
        headers.ContentType = contentType;

        if (stream.CanSeek)
        {
          stream.Position = 0;
        }

        var response = await blobClient.UploadAsync(stream, headers);

        _logger.LogInformation("Successfully uploaded blob {BlobName}, Size: {SizeKB}KB", blobName, sizeKb);
        return new BlobModel(blobName, blobClient.Uri.AbsoluteUri, sizeKb)
        {
          ETag = response.Value.ETag.ToString()
        };
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to upload blob {BlobName} to container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<BlobModel> UpdateBlobAsync(string containerName,
      string blobName,
      Stream stream,
      string contentType = BlobContentType.Octet,
      string connectionString = "")
    {
      _logger.LogInformation("Updating blob {BlobName} in container {ContainerName}", blobName, containerName);
      return await AddBlobAsync(containerName, blobName, stream, contentType, connectionString);
    }

    public async Task<BlobConditionalWriteResult> UpdateBlobIfUnchangedAsync(string containerName,
      string blobName,
      Stream stream,
      string expectedETag,
      string contentType = BlobContentType.Octet,
      string connectionString = "")
    {
      try
      {
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var headers = new BlobHttpHeaders();
        headers.ContentType = contentType;

        if (stream.CanSeek)
        {
          stream.Position = 0;
        }

        BlobRequestConditions conditions = expectedETag == null
          ? new BlobRequestConditions { IfNoneMatch = ETag.All }
          : new BlobRequestConditions { IfMatch = new ETag(expectedETag) };

        var options = new BlobUploadOptions
        {
          HttpHeaders = headers,
          Conditions = conditions
        };

        var response = await blobClient.UploadAsync(stream, options);

        _logger.LogInformation("Conditionally updated blob {BlobName} in container {ContainerName}", blobName, containerName);

        return new BlobConditionalWriteResult
        {
          Success = true,
          Blob = new BlobModel(blobName, blobClient.Uri.AbsoluteUri)
          {
            ETag = response.Value.ETag.ToString()
          }
        };
      }
      catch (RequestFailedException ex) when (ex.Status == 412)
      {
        // A concurrent writer changed the blob (or created/removed it) since the caller last
        // observed its state. Not an error - the caller reacts by re-reading and retrying.
        _logger.LogInformation("Conditional write to blob {BlobName} in container {ContainerName} lost a concurrent write race.", blobName, containerName);
        return new BlobConditionalWriteResult { Success = false };
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to conditionally upload blob {BlobName} to container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<bool> DeleteBlobAsync(string containerName,
      string blobName,
      string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Deleting blob {BlobName} from container {ContainerName}", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);

        var deleted = await blobClient.DeleteIfExistsAsync();

        if (deleted)
        {
          _logger.LogInformation("Successfully deleted blob {BlobName}", blobName);
        }
        else
        {
          _logger.LogWarning("Blob {BlobName} did not exist", blobName);
        }

        return deleted;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to delete blob {BlobName} from container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task ClearContainerAsync(string containerName, string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Clearing all blobs from container {ContainerName}", containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        BlobBatchClient batchClient = serviceClient.GetBlobBatchClient();

        List<Uri> uris = new List<Uri>();
        var blobs = await GetBlobsAsync(containerName);
        var totalBlobs = blobs.Count;
        int deletedCount = 0;

        foreach (var blob in blobs)
        {
          BlobClient blobClient = containerClient.GetBlobClient(blob.Name);
          uris.Add(blobClient.Uri);

          if (uris.Count % 256 == 0)
          {
            await batchClient.DeleteBlobsAsync(uris);
            deletedCount += uris.Count;
            _logger.LogDebug("Deleted {DeletedCount}/{TotalCount} blobs", deletedCount, totalBlobs);
            uris.Clear();
          }
        }

        if (uris.Any())
        {
          await batchClient.DeleteBlobsAsync(uris);
          deletedCount += uris.Count;
          uris.Clear();
        }

        _logger.LogInformation("Successfully cleared {DeletedCount} blobs from container {ContainerName}", deletedCount, containerName);
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to clear container {ContainerName}", containerName);
        throw;
      }
    }

    public async Task DeleteFolderContentsAsync(string containerName, string folderPath, string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Deleting folder contents at {FolderPath} in container {ContainerName}", folderPath, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);

        int deletedCount = 0;
        await foreach(BlobItem blob in containerClient.GetBlobsAsync(BlobTraits.None, BlobStates.None, folderPath, default))
        {
          if(!blob.Name.Equals(folderPath, StringComparison.OrdinalIgnoreCase))
          {
            await containerClient.GetBlobClient(blob.Name).DeleteIfExistsAsync();
            deletedCount++;
          }
        }

        _logger.LogInformation("Deleted {DeletedCount} blobs from folder {FolderPath}", deletedCount, folderPath);
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to delete folder contents at {FolderPath} in container {ContainerName}", folderPath, containerName);
        throw;
      }
    }

    public async Task DeleteFolderAsync(string containerName, string folderPath, string connectionString = "")
    {
      try
      {
        _logger.LogInformation("Deleting folder {FolderPath} in container {ContainerName}", folderPath, containerName);
        await DeleteFolderContentsAsync(containerName, folderPath, connectionString);

        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);

        bool isFolderEmpty = true;
        await foreach(BlobItem blob in containerClient.GetBlobsAsync(BlobTraits.None, BlobStates.None, folderPath, default))
        {
          if(!blob.Name.Equals(folderPath, StringComparison.OrdinalIgnoreCase))
          {
            isFolderEmpty = false;
            break;
          }
        }

        if(isFolderEmpty)
        {
          await containerClient.GetBlobClient(folderPath).DeleteIfExistsAsync();
          _logger.LogInformation("Successfully deleted folder {FolderPath}", folderPath);
        }
        else
        {
          _logger.LogWarning("Folder {FolderPath} not empty after deleting contents", folderPath);
        }
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to delete folder {FolderPath} in container {ContainerName}", folderPath, containerName);
        throw;
      }
    }

    public async Task<long> GetBlobSizeAsync(string containerName, string blobName, string connectionString = "")
    {
      try
      {
        _logger.LogDebug("Getting size of blob {BlobName} in container {ContainerName}", blobName, containerName);
        var serviceClient = CreateServiceClient(connectionString);
        var containerClient = CreateContainerClient(serviceClient, containerName);
        var blobClient = CreateBlobClient(containerClient, containerName, blobName);
        var props = await blobClient.GetPropertiesAsync();
        var sizeBytes = props.Value.ContentLength;

        _logger.LogDebug("Blob {BlobName} size: {SizeBytes} bytes ({SizeKB}KB)", blobName, sizeBytes, sizeBytes / 1024);
        return sizeBytes;
      }
      catch (Exception ex)
      {
        _logger.LogError(ex, "Failed to get size of blob {BlobName} in container {ContainerName}", blobName, containerName);
        throw;
      }
    }

    public async Task<string> GetBlobETagAsync(string containerName, string blobName, string connectionString = "")
    {
      var serviceClient = CreateServiceClient(connectionString);
      var containerClient = CreateContainerClient(serviceClient, containerName);
      var blobClient = CreateBlobClient(containerClient, containerName, blobName);
      var props = await blobClient.GetPropertiesAsync();
      return props.Value.ETag.ToString();
    }

    /// <summary>
    /// Gets a cached BlobServiceClient using the ClientManager
    /// Uses managed identity or key access depending on the connection string
    /// </summary>
    private BlobServiceClient CreateServiceClient(string connectionString = null)
    {
      return _clientManager.GetServiceClient(connectionString);
    }

    private BlobContainerClient CreateContainerClient(BlobServiceClient serviceClient, string containerName)
    {
      containerName = GetContainerName(containerName);
      return serviceClient.GetBlobContainerClient(containerName);
    }

    private BlobClient CreateBlobClient(BlobContainerClient containerClient, string containerName, string blobName)
    {
      var prefix = GetBlobPrefix(containerName);
      blobName = prefix.HasValue() && !blobName.Contains("/") ? $"{prefix}/{blobName}" : blobName;

      return containerClient.GetBlobClient(blobName);
    }

    /// <summary>
    /// The container name can only be the first part of a path before the first /
    /// </summary>
    /// <param name="input"></param>
    /// <returns></returns>
    private string GetContainerName(string input)
    {
      string container = input;

      if (input.Contains("/"))
      {
        container = input.Substring(0, input.IndexOf("/"));
      }
      
      return container;
    }

    /// <summary>
    /// The blob name can be the part of the path after the first / plus the blob name
    /// </summary>
    /// <param name="containerName"></param>
    /// <returns></returns>
    private string GetBlobPrefix(string containerName)
    {
      string prefix = null;

      if (containerName.Contains("/"))
      {
        prefix = containerName.Substring(containerName.IndexOf("/") + 1);
      }

      return prefix;
    }

    private string GetAccountKey(string cn)
    {
      var parts = cn.Split(new char[] { ';' }, StringSplitOptions.RemoveEmptyEntries);

      foreach (string part in parts)
      {
        var values = part.Split(['='], 2);
        if (values.Length != 2)
        {
          throw new Exception("Storage account settings must be of form \"name=value\"");
        }
        if (values[0].ToLower() == "accountkey")
        {
          return values[1].Trim();
        }
      }

      throw new Exception("Could not get account key from storage connection");
    }

  }
}
