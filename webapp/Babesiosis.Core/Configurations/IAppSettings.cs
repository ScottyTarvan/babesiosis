using Babesiosis.Core.Configurations.Configurations;
using BlobStorageConfiguration = Babesiosis.Core.Configurations.Configurations.BlobStorageConfiguration;
using EventGridConfiguration = Babesiosis.Core.Configurations.Configurations.EventGridConfiguration;

namespace Babesiosis.Core.Configurations
{
  public interface IAppSettings
  {
    ConnectionsConfiguration Connections { get; }
    ContainersConfiguration Containers { get; }
    JwtConfiguration Jwt { get; }
    MjmlApiConfiguration MjmlApi { get; }
    AiAgentsConfiguration AiAgents { get; }
    QueuesConfiguration Queues { get; }
    SecurityConfiguration Security { get; }
    GraphConfiguration Graph { get; }
    AzureCommunicationEmailConfiguration AzureCommunicationEmail { get; }
    WebAppConfiguration WebApp { get; }
    PPSConfiguration PPS { get; }
    ProxyConfiguration Proxy { get; }
    AzureTenantConfiguration AzureTenant { get; }
    ReportTransformsConfiguration ReportTransforms { get; }
    EventGridConfiguration EventGrid { get; }
    BlobStorageConfiguration BlobStorage { get; }
    KeyVaultConfiguration KeyVault { get; }
    ServiceBusConfiguration ServiceBus { get; }
    ExpectationsConfiguration Expectations { get; }
  }
}