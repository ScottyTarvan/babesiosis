using Babesiosis.Core.Models.Email;
using Babesiosis.Core.Models.Teams;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Services
{
    public interface IEmailFactory
  {
    Task<Email> CreateForgotPasswordEmailAsync(User user, string token);
  }
}
