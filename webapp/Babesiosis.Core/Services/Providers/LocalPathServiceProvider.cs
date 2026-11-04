using Babesiosis.Core.Services.Impl;

namespace Babesiosis.Core.Services.Providers
{
  public static class LocalPathServiceProvider
  {
    public static ILocalPathService GetService(string path)
    {
      return new LocalPathService(path);
    }
  }
}
