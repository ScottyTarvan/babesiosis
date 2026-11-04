using System;

namespace Babesiosis.Core.Configurations.Configurations
{
  public class PPSConfiguration
  {
    public Guid DatabaseLinkedServiceId { get; set; }
    public string FactsetUserName { get; set; }
    public string FactsetAPIKey { get; set; }
    public Guid StorageLinkedServiceId { get; set; }
    public string MergedClassificationPath { get; set; }
    public int FactsetBatchSize { get; set; }
  }
}
