using System;
using System.Collections.Generic;

namespace Babesiosis.Core.Models.Email
{
  public class Email
  {
    public int Id { get; set; }
    public string FromAddress { get; set; }
    public string ToAddress { get; set; }
    public string Subject { get; set; }
    public string Body { get; set; }
    public DateTime CreatedDate { get; set; }
    public IEnumerable<EmailFileAttachment> Attachments { get; set; } = new List<EmailFileAttachment>();
  }
}
