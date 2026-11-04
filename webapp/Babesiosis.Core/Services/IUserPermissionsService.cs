using System;

namespace Babesiosis.Core.Services
{
  public interface IUserPermissionsService
  {
    bool Can(Guid userId, string action, string subject);
    void Assert(Guid userId, string action, string subject);
    bool IsAdministrator(Guid userId);
  }
}
