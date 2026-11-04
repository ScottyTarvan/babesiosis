using System.Threading.Tasks;
using Babesiosis.Core.Configurations;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Queue;

namespace Babesiosis.Core.Services.Impl
{
    internal class AzureQueueStorageService : IQueueStorageService
    {
        private readonly IAppSettings _appSettings;
        private readonly CloudStorageAccount _storageAccount;

        internal AzureQueueStorageService(IAppSettingsService appSettingsService)
        {
            _appSettings = appSettingsService.GetAppSettings();
            _storageAccount = CloudStorageAccount.Parse(_appSettings.Connections.Storage);
        }

        public async Task AddMessageAsync(string queueName, string message)
        {
            var queue = GetQueue(queueName);
            var cloudMessage = new CloudQueueMessage(message);
            await queue.AddMessageAsync(cloudMessage);
        }

        public async Task<string> PeekMessageAsync(string queueName)
        {
            var queue = GetQueue(queueName);
            var message = await queue.PeekMessageAsync();
            return message.AsString;
        }

        public async Task<string> GetMessageAsync(string queueName)
        {
            var queue = GetQueue(queueName);
            var message = await queue.GetMessageAsync();
            return message.AsString;
        }

        private CloudQueue GetQueue(string queueName)
        {
            var client = _storageAccount.CreateCloudQueueClient();
            return client.GetQueueReference(queueName);
        }
    }
}
