using Babesiosis.Core.Models.Email;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
    public interface IEmailService
  {
    Task SendAsync(Email email);
  }
}
