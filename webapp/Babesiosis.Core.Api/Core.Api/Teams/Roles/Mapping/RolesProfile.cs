using AutoMapper;
using Babesiosis.Core.Api.Teams.Roles.ViewModels;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using System.Linq;

namespace Babesiosis.Core.Api.Teams.Roles.Mapping
{
  public class RolesProfile : Profile
  {
    public RolesProfile()
    {
      CreateMap<Role, RoleViewModel>()
        .ForMember(dest => dest.RowVersion, o => o.MapFrom(src => src.RowVersion.ToBase64String()))
        .ForMember(dest => dest.HasPermissions, o => o.MapFrom(src => src.Permissions.Any()));

      CreateMap<RoleViewModel, Role>()
        .ForMember(dest => dest.RowVersion, o => o.MapFrom(src => src.RowVersion.FromBase64String()));
    }
  }
}
