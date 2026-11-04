using Babesiosis.Core.Models.Events;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
  public interface IEventGridService
  {
    Task Connect(string endPoint, string accessKey);
    Task PublishEventAsync(EventMessage message, string endPoint = null, string accessKey = null);
  }
}
