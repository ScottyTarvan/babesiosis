using Babesiosis.Core.Models.Domain;
using Microsoft.Data.SqlClient;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Babesiosis.Core.Extensions
{
  public static class SqlConnectionStringBuilderExtensions
  {
    public static bool IsSqlAuthentication(this SqlConnectionStringBuilder builder)
    {
      return (builder.Authentication == SqlAuthenticationMethod.SqlPassword || builder.Authentication == SqlAuthenticationMethod.NotSpecified)
        && builder.UserID.HasValue()
        && builder.Password.HasValue();
    }
  }
}
