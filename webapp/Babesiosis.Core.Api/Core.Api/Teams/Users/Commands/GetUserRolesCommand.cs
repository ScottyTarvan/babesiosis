using System;
using DevExtreme.AspNet.Data;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Api.Teams.Users.Commands
{
  public class GetUserRolesCommand
  {
    public Guid UserId { get; set; }
    public DataSourceLoadOptionsBase LoadOptions { get; set; }
  }
}
