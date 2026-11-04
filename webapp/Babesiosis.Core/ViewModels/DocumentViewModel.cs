using Babesiosis.Core.Models.Domain;
using System.IO;

namespace Babesiosis.Core.ViewModels
{
    public class DocumentViewModel : ViewModel
  {
    public string FileName { get; set; }
    public double FilesizeKb { get; set; }
    public string FileType { get; set; }
    public string ExternalStoreId { get; set; }

    public EditState EditState { get; set; }
    public string FileId { get; set; }
    public string BlobLink { get; set; }
    public Stream Stream { get; set; }
  }
}
