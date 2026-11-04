using Microsoft.Extensions.Logging;

namespace Babesiosis.Core.Functions
{
  public abstract class ServiceBusFunctionBase : FunctionBase
  {
    private readonly ILogger _logger;

    public ServiceBusFunctionBase(ILogger logger)
    {
      _logger = logger;
    }

    protected ILogger Logger => _logger;
  }
}
