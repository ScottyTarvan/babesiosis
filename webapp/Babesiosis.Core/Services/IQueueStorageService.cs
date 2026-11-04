using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface IQueueStorageService
  {
    Task AddMessageAsync(string queueName, string message);
    Task<string> PeekMessageAsync(string queueName);
    Task<string> GetMessageAsync(string queueName);
  }
}
