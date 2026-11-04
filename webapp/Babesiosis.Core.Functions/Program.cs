using Babesiosis.Core.Api.Hosting;
using Babesiosis.Core.Functions;
using Babesiosis.Core.Functions.Middleware;
using Microsoft.Azure.Functions.Worker;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

internal class Program
{
  private static void Main(string[] args)
  {
    AppDomain.CurrentDomain.UnhandledException += (sender, args) =>
    {
      Console.WriteLine($"Unhandled Exception: {args.ExceptionObject}");
      Console.ReadLine();
    };

    var host = new HostBuilder()
    // The permission middleware is a no-op for any function without a
    // [RequiredPermission] attribute, which is every pre-existing endpoint.
    // MCP tools are served by the dedicated MCP application (Babesiosis.Mcp.Functions,
    // platform/mcp-server.md §3.1); this app keeps the personal access token endpoints.
    .ConfigureFunctionsWebApplication(worker =>
    {
      worker.UseMiddleware<RequiredPermissionsMiddleware>();
    })
    .ConfigureServices(services =>
    {
      services.AddApplicationInsightsTelemetryWorkerService();
      services.ConfigureFunctionsApplicationInsights();
      services.AddLogging();

      // Settings, AutoMapper and the platform and permission services every controller
      // depends on. The scan below registers only the controllers themselves.
      services.AddBabesiosisCore();

      RegisterControllers(services);
    })
    .ConfigureLogging(logging =>
    {
      logging.AddConsole();
    })
    .Build();

    host.Run();
  }

  private static void RegisterControllers(IServiceCollection services)
  {
    var types = typeof(Program).Assembly
      .GetTypes()
      .Where(t => t.IsClass
      && !t.IsAbstract
      && t.IsSubclassOf(typeof(FunctionBase)));

    foreach (var type in types)
    {
      var ctors = type.GetConstructors();

      foreach (var ctor in ctors)
      {
        var prams = ctor.GetParameters();
        foreach (var pram in prams)
        {
          var pramType = pram.ParameterType;
          if (pramType.Name.Contains("Controller"))
          {
            services.Add(new ServiceDescriptor(pramType, pramType, ServiceLifetime.Transient));
          }
        }
      }
    }
  }
}
