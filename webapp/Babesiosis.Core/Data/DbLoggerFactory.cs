using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Debug;

namespace Babesiosis.Core.Data
{
  internal static class DbLoggerFactory
  {
    // A single, shared instance: EF Core hashes the ILoggerFactory reference passed to
    // UseLoggerFactory when deciding whether it can reuse its cached internal service
    // provider. A fresh instance per call (the previous behaviour here) forces EF to
    // rebuild that provider - including the full compiled model - on every DbContext
    // creation, which is every request through IDbContextService.
    private static readonly LoggerFactory _instance = new LoggerFactory(new[] { new DebugLoggerProvider() });

    internal static LoggerFactory Create() => _instance;
  }
}
