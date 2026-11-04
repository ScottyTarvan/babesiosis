using AutoMapper;
using Babesiosis.Core.Extensions;
using Babesiosis.Core.Models.Teams;
using Babesiosis.Core.ViewModels;

namespace Babesiosis.Core.Api.Auth.Mapping
{
  public class AuthProfile : Profile
  {
    public AuthProfile()
    {
      CreateMap<User, UserViewModel>()
           .ForMember(dest => dest.RowVersion, o => o.MapFrom(src => src.RowVersion.ToBase64String()))
           .ForMember(dest => dest.Password, o => o.Ignore());

      CreateMap<UserViewModel, User>()
        .ForMember(dest => dest.RowVersion, o => o.MapFrom(src => src.RowVersion.FromBase64String()))
        .ForMember(dest => dest.CreatedDate, o => o.Ignore())
        .ForMember(dest => dest.Password, o => o.Ignore())
        // Elevation and deletion go through their own guarded paths — a posted UserViewModel
        // must never be able to set these directly through this map either (both profiles'
        // CreateMap<UserViewModel, User> load into the same AutoMapper configuration).
        .ForMember(dest => dest.IsSuperAdministrator, o => o.Ignore())
        .ForMember(dest => dest.IsDeleted, o => o.Ignore());

    }
  }
}
