using Babesiosis.Core.Models.Domain;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.ViewModels;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Babesiosis.Core.Teams.Services
{
  public interface ITeamsService
  {
    Task<User> GetUserAync(Guid userId);
    Task<User> GetUserAync(int userId);
  }
}
