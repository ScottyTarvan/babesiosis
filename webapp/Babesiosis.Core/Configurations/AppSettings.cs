using Babesiosis.Core.Configurations.Configurations;
using Babesiosis.Core.Extensions;
using Microsoft.Extensions.Configuration;
using System;

namespace Babesiosis.Core.Configurations
{
  public class AppSettings : IAppSettings
  {
    private IConfiguration _configuration;
    
    public AppSettings(IConfiguration configuration)
    {
      this._configuration = configuration;
    }

    public ConnectionsConfiguration Connections
    {
      get
      {
        return new ConnectionsConfiguration()
        {
          Database = this._configuration["AppSettings:Connections:Database"],
          Storage = this._configuration["AppSettings:Connections:Storage"],
          ServiceBus = this._configuration["AppSettings:Connections:ServiceBus"],
          KeyVault = this._configuration["AppSettings:Connections:KeyVault"]
        };
      }
    }

    public ContainersConfiguration Containers
    {
      get
      {
        return new ContainersConfiguration()
        {
          PermissionsCache = this._configuration["AppSettings:Containers:PermissionsCache"],
          SsoLogin = this._configuration["AppSettings:Containers:SsoLogin"],
          Avatars = this._configuration["AppSettings:Containers:Avatars"],
          DatasetSnapshots = this._configuration["AppSettings:Containers:DatasetSnapshots"],
          DatasetLinks = this._configuration["AppSettings:Containers:DatasetLinks"],
          Reports = this._configuration["AppSettings:Containers:Reports"],
          ReportTemplates = this._configuration["AppSettings:Containers:ReportTemplates"],
          ReportImages = this._configuration["AppSettings:Containers:ReportImages"],
          ReportPdfs = this._configuration["AppSettings:Containers:ReportPdfs"],
          ReportFonts = this._configuration["AppSettings:Containers:ReportFonts"],
          ReportSnapshots = this._configuration["AppSettings:Containers:ReportSnapshots"]
        };
      }
    }

    public JwtConfiguration Jwt
    {
      get
      {
        return new JwtConfiguration()
        {
          Audience = this._configuration["AppSettings:Jwt:Audience"],
          ExpiryTimeSpan = TimeSpan.Parse(this._configuration["AppSettings:Jwt:ExpiryTimeSpan"]),
          Issuer = this._configuration["AppSettings:Jwt:Issuer"],
          SecurityKey = this._configuration["AppSettings:Jwt:SecurityKey"],
          RefreshTokenExpiryTimeSpan = TimeSpan.Parse(this._configuration["AppSettings:Jwt:RefreshTokenExpiryTimeSpan"]),
        };
      }
    }

    public MjmlApiConfiguration MjmlApi
    {
      get
      {
        return new MjmlApiConfiguration()
        {
          ApiUrl = this._configuration["AppSettings:MjmlApi:ApiUrl"],
          ApplicationId = this._configuration["AppSettings:MjmlApi:ApplicationId"],
          ApiKey = this._configuration["AppSettings:MjmlApi:ApiKey"],
          EmailAssetsUrl = this._configuration["AppSettings:MjmlApi:EmailAssetsUrl"]
        };
      }
    }

    // Read on every access so a configuration refresh swaps a tier mapping without a restart.
    // String values are trimmed: a trailing CR/LF in an App Configuration value breaks keys and URLs.
    public AiAgentsConfiguration AiAgents
    {
      get
      {
        string Read(string key) => this._configuration[$"AppSettings:AiAgents:{key}"]?.Trim();

        return new AiAgentsConfiguration()
        {
          Enabled = bool.TryParse(Read("Enabled"), out var enabled) && enabled,
          ApiKey = Read("ApiKey"),
          BaseUrl = Read("BaseUrl").HasValue() ? Read("BaseUrl") : AiAgentsConfiguration.DefaultBaseUrl,
          TimeoutSeconds = int.TryParse(Read("TimeoutSeconds"), out var timeout) && timeout > 0
            ? timeout : AiAgentsConfiguration.DefaultTimeoutSeconds,
          Models = new AiAgentsModelsConfiguration()
          {
            Low = Read("Models:Low"),
            Medium = Read("Models:Medium"),
            High = Read("Models:High"),
            Max = Read("Models:Max")
          },
          BodyStorageAllowed = bool.TryParse(Read("BodyStorageAllowed"), out var bodies) && bodies,
          // On unless explicitly turned off.
          FullText = !bool.TryParse(Read("FullText"), out var fullText) || fullText
        };
      }
    }

    public QueuesConfiguration Queues
    {
      get
      {
        return new QueuesConfiguration()
        {
          Email = this._configuration["AppSettings:Queues:EmailQueue"],
          Deployment = this._configuration["AppSettings:Queues:Deployment"],
          DeploymentTrigger = this._configuration["AppSettings:Queues:DeploymentTrigger"],
          ReportExecution = this._configuration["AppSettings:Queues:ReportExecution"],
          ReportBatch = this._configuration["AppSettings:Queues:ReportBatch"],
          EventTrigger = this._configuration["AppSettings:Queues:EventTrigger"],
          PipelineLog = this._configuration["AppSettings:Queues:PipelineLog"],
          PermissionsCacheRetry = this._configuration["AppSettings:Queues:PermissionsCacheRetry"],
          ExpectationResult = this._configuration["AppSettings:Queues:ExpectationResult"]
        };
      }
    }

    public SecurityConfiguration Security
    {
      get
      {
        return new SecurityConfiguration()
        {
          EncryptionKey = this._configuration["AppSettings:Security:EncryptionKey"],
          ResetPasswordExpiryTimeSpan = TimeSpan.Parse(this._configuration["AppSettings:Security:ResetPasswordExpiryTimeSpan"]),
          ReCaptchaSecretKey = this._configuration["AppSettings:Security:ReCaptchaSecretKey"],
          EntraIdTenantId = this._configuration["AppSettings:Security:EntraIdTenantId"],
          EntraIdClientId = this._configuration["AppSettings:Security:EntraIdClientId"],
          EntraIdClientSecret = this._configuration["AppSettings:Security:EntraIdClientSecret"],
          EntraIdRedirectUri = this._configuration["AppSettings:Security:EntraIdRedirectUri"]
        };
      }
    }

    public EventGridConfiguration EventGrid
    {
      get
      {
        return new EventGridConfiguration()
        {
          EndPoint = this._configuration["AppSettings:EventGrid:Endpoint"],
          Key = this._configuration["AppSettings:EventGrid:Key"],
          MaxRetries = int.TryParse(this._configuration["AppSettings:EventGrid:MaxRetries"], out var maxRetries) ? maxRetries : 3,
          RetryDelaySeconds = int.TryParse(this._configuration["AppSettings:EventGrid:RetryDelaySeconds"], out var retryDelay) ? retryDelay : 2,
          MaxRetryDelaySeconds = int.TryParse(this._configuration["AppSettings:EventGrid:MaxRetryDelaySeconds"], out var maxRetryDelay) ? maxRetryDelay : 30,
          RetryMode = this._configuration["AppSettings:EventGrid:RetryMode"] ?? "Exponential",
          OperationTimeoutSeconds = int.TryParse(this._configuration["AppSettings:EventGrid:OperationTimeoutSeconds"], out var timeout) ? timeout : 120,
          UseKeyBasedAuth = bool.TryParse(this._configuration["AppSettings:EventGrid:UseKeyBasedAuth"], out var useKeyAuth) ? useKeyAuth : true,
          TenantId = this._configuration["AppSettings:EventGrid:TenantId"] ?? Environment.GetEnvironmentVariable("AZURE_TENANT_ID"),
          ManagedIdentityClientId = this._configuration["AppSettings:EventGrid:ManagedIdentityClientId"]
        };
      }
    }

    //https://medium.com/medialesson/convert-files-to-pdf-using-microsoft-graph-azure-functions-20bc84d2adc4
    public GraphConfiguration Graph
    {
      get
      {
        return new GraphConfiguration()
        {
          EndPoint = this._configuration["AppSettings:Graph:EndPoint"],
          GraphEndPoint = this._configuration["AppSettings:Graph:GraphEndPoint"],
          GrantType = this._configuration["AppSettings:Graph:GrantType"],
          Scope = this._configuration["AppSettings:Graph:Scope"],
          Resource = this._configuration["AppSettings:Graph:Resource"],
          TenantId = this._configuration["AppSettings:Graph:TenantId"],
          ClientId = this._configuration["AppSettings:Graph:ClientId"],
          ClientSecret = this._configuration["AppSettings:Graph:ClientSecret"],
          SiteId = this._configuration["AppSettings:Graph:SiteId"]
        };
      }
    }

    public AzureCommunicationEmailConfiguration AzureCommunicationEmail
    {
      get
      {
        return new AzureCommunicationEmailConfiguration()
        {
          ConnectionString = this._configuration["AppSettings:AzureCommunicationEmail:ConnectionString"],
          SenderAddress = this._configuration["AppSettings:AzureCommunicationEmail:SenderAddress"]
        };
      }
    }

    public WebAppConfiguration WebApp
    {
      get
      {
        return new WebAppConfiguration()
        {
          Url = this._configuration["AppSettings:WebApp:Url"]
        };
      }
    }

    public PPSConfiguration PPS
    {
      get
      {
        return new PPSConfiguration()
        {
          DatabaseLinkedServiceId = Guid.Parse(this._configuration["AppSettings:PPS:DatabaseLinkedServiceId"]),
          FactsetUserName = this._configuration["AppSettings:PPS:FactsetUserName"],
          FactsetAPIKey = this._configuration["AppSettings:PPS:FactsetAPIKey"],
          StorageLinkedServiceId = Guid.Parse(this._configuration["AppSettings:PPS:StorageLinkedServiceId"]),
          MergedClassificationPath = this._configuration["AppSettings:PPS:MergedClassificationPath"],
          FactsetBatchSize = int.Parse(this._configuration["AppSettings:PPS:FactsetBatchSize"])
        };
      }
    }

    public ProxyConfiguration Proxy
    {
      get
      {
        return new ProxyConfiguration()
        {
          CoreApiUrl = this._configuration["AppSettings:Proxy:CoreApiUrl"],
          CoreApiKey = this._configuration["AppSettings:Proxy:CoreApiKey"],
          ReportsApiUrl = this._configuration["AppSettings:Proxy:ReportsApiUrl"],
          ReportsApiKey = this._configuration["AppSettings:Proxy:ReportsApiKey"],
          AllowedOrigins = this._configuration["AppSettings:Proxy:AllowedOrigins"]
        };
      }
    }

    public AzureTenantConfiguration AzureTenant
    {
      get
      {
        return new AzureTenantConfiguration()
        {
          TenantId = this._configuration["AppSettings:AzureTenant:TenantId"]
        };
      }
    }

    public ReportTransformsConfiguration ReportTransforms
    {
      get
      {
        return new ReportTransformsConfiguration()
        {
          CommandTimeoutSeconds = this._configuration["AppSettings:ReportTransforms:CommandTimeoutSeconds"].HasValue() ?
            int.Parse(this._configuration["AppSettings:ReportTransforms:CommandTimeoutSeconds"]) : 30,
          TestCommandTimeoutSeconds = this._configuration["AppSettings:ReportTransforms:TestCommandTimeoutSeconds"].HasValue() ?
            int.Parse(this._configuration["AppSettings:ReportTransforms:TestCommandTimeoutSeconds"]) : 15,
          TestRowLimit = this._configuration["AppSettings:ReportTransforms:TestRowLimit"].HasValue() ?
            int.Parse(this._configuration["AppSettings:ReportTransforms:TestRowLimit"]) : 20
        };
      }
    }

    public BlobStorageConfiguration BlobStorage
    {
      get
      {
        return new BlobStorageConfiguration()
        {
          MaxRetries = int.TryParse(this._configuration["AppSettings:BlobStorage:MaxRetries"], out var maxRetries) ? maxRetries : 3,
          RetryDelaySeconds = int.TryParse(this._configuration["AppSettings:BlobStorage:RetryDelaySeconds"], out var retryDelay) ? retryDelay : 2,
          OperationTimeoutSeconds = int.TryParse(this._configuration["AppSettings:BlobStorage:OperationTimeoutSeconds"], out var timeout) ? timeout : 120,
          DefaultSasExpirationHours = int.TryParse(this._configuration["AppSettings:BlobStorage:DefaultSasExpirationHours"], out var sasHours) ? sasHours : 24,
          NonExpiringSasExpirationYears = int.TryParse(this._configuration["AppSettings:BlobStorage:NonExpiringSasExpirationYears"], out var sasYears) ? sasYears : 5,
          BatchOperationSize = int.TryParse(this._configuration["AppSettings:BlobStorage:BatchOperationSize"], out var batchSize) ? batchSize : 256,
          EnableContentValidation = bool.TryParse(this._configuration["AppSettings:BlobStorage:EnableContentValidation"], out var validation) && validation,
          TenantId = this._configuration["AppSettings:BlobStorage:TenantId"] ?? Environment.GetEnvironmentVariable("AZURE_TENANT_ID"),
          ManagedIdentityClientId = this._configuration["AppSettings:BlobStorage:ManagedIdentityClientId"]
        };
      }
    }

    public KeyVaultConfiguration KeyVault
    {
      get
      {
        return new KeyVaultConfiguration()
        {
          MaxRetries = int.TryParse(this._configuration["AppSettings:KeyVault:MaxRetries"], out var maxRetries) ? maxRetries : 5,
          RetryDelaySeconds = int.TryParse(this._configuration["AppSettings:KeyVault:RetryDelaySeconds"], out var retryDelay) ? retryDelay : 2,
          MaxRetryDelaySeconds = int.TryParse(this._configuration["AppSettings:KeyVault:MaxRetryDelaySeconds"], out var maxRetryDelay) ? maxRetryDelay : 16,
          RetryMode = this._configuration["AppSettings:KeyVault:RetryMode"] ?? "Exponential",
          OperationTimeoutSeconds = int.TryParse(this._configuration["AppSettings:KeyVault:OperationTimeoutSeconds"], out var timeout) ? timeout : 120,
          TenantId = this._configuration["AppSettings:KeyVault:TenantId"] ?? Environment.GetEnvironmentVariable("AZURE_TENANT_ID"),
          ManagedIdentityClientId = this._configuration["AppSettings:KeyVault:ManagedIdentityClientId"]
        };
      }
    }

    public ServiceBusConfiguration ServiceBus
    {
      get
      {
        return new ServiceBusConfiguration()
        {
          MaxRetries = int.TryParse(this._configuration["AppSettings:ServiceBus:MaxRetries"], out var maxRetries) ? maxRetries : 3,
          MaxDelaySeconds = int.TryParse(this._configuration["AppSettings:ServiceBus:MaxDelaySeconds"], out var maxDelay) ? maxDelay : 30,
          RetryMode = this._configuration["AppSettings:ServiceBus:RetryMode"] ?? "Exponential",
          NetworkTimeoutSeconds = int.TryParse(this._configuration["AppSettings:ServiceBus:NetworkTimeoutSeconds"], out var timeout) ? timeout : 120,
          TenantId = this._configuration["AppSettings:ServiceBus:TenantId"] ?? Environment.GetEnvironmentVariable("AZURE_TENANT_ID"),
          ManagedIdentityClientId = this._configuration["AppSettings:ServiceBus:ManagedIdentityClientId"]
        };
      }
    }

    public ExpectationsConfiguration Expectations
    {
      get
      {
        return new ExpectationsConfiguration()
        {
          RetentionDays = int.TryParse(this._configuration["AppSettings:Expectations:RetentionDays"], out var retentionDays) ? retentionDays : 7,
          ExceptionRowCap = int.TryParse(this._configuration["AppSettings:Expectations:ExceptionRowCap"], out var exceptionRowCap) ? exceptionRowCap : 500,
          Container = this._configuration["AppSettings:Expectations:Container"]
        };
      }
    }
  }
}
