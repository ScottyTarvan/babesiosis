using Microsoft.AspNetCore.Mvc;
using System.Threading.Tasks;

namespace Babesiosis.Core.Functions
{
  public class ServerErrorResult : ObjectResult
  {
    public ServerErrorResult(object value) : base(value)
    {
      Value = value;
      StatusCode = 500;
    }

    public override bool Equals(object obj)
    {
      return base.Equals(obj);
    }

    public override void ExecuteResult(ActionContext context)
    {
      base.ExecuteResult(context);
    }

    public override Task ExecuteResultAsync(ActionContext context)
    {
      return base.ExecuteResultAsync(context);
    }

    public override int GetHashCode()
    {
      return base.GetHashCode();
    }

    public override void OnFormatting(ActionContext context)
    {
      base.OnFormatting(context);
    }

    public override string ToString()
    {
      return base.ToString();
    }
  }
}
