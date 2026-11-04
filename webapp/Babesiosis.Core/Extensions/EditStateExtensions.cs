using Babesiosis.Core.Models.Domain;
using Microsoft.EntityFrameworkCore;

namespace Babesiosis.Core.Extensions
{
    public static class EditStateExtensions
  {
    public static EntityState ToDbState(this EditState editState)
    {
      EntityState state = EntityState.Unchanged;

      switch (editState)
      {
        case (EditState.Added):
          state = EntityState.Added;
          break;
        case (EditState.Deleted):
          state = EntityState.Deleted;
          break;
        case (EditState.Detached):
          state = EntityState.Detached;
          break;
        case (EditState.Modified):
          state = EntityState.Modified;
          break;
      }

      return state;
    }
  }
}
