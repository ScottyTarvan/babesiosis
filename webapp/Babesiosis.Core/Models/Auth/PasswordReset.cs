using System;
using Babesiosis.Core.Models.Domain;
using Babesiosis.Core.Models.Teams;

namespace Babesiosis.Core.Models.Auth
{
    public class PasswordReset : IdModel
  {
    public int UserId { get; set; }
    public DateTime CreatedDate { get; set; } = DateTime.UtcNow;
    public Guid Token { get; set; }

    public User User { get; set; }
  }
}
