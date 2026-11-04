namespace Babesiosis.Core.Services.Impl
{
  internal class LocalPathService : ILocalPathService
  {
    public LocalPathService(string localPath)
    {
      LocalPath = localPath;
    }

    public string LocalPath { get; set; }
  }
}
