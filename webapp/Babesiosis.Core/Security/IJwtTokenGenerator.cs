using System;

namespace Babesiosis.Core.Security
{
  public interface IJwtTokenGenerator
  {
    string CreateToken(Guid userId, TimeSpan timeTillExpires);

    bool ValidateToken(string token);

    Guid GetUserId(string token);
  }
}
