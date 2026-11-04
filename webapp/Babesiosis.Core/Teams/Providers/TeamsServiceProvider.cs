using AutoMapper;
using Babesiosis.Core.Configurations;
using Babesiosis.Core.Data;
using Babesiosis.Core.Services;
using Babesiosis.Core.Teams.Impl;
using System;

namespace Babesiosis.Core.Teams.Services.Providers
{
  public static class TeamsServiceProvider
  {
    public static ITeamsService GetService(IServiceProvider services)
    {
      IDbContextService dbContextService = services.GetService(typeof(IDbContextService)) as IDbContextService;
      
      return new TeamsService(dbContextService);
    }
  }
}
