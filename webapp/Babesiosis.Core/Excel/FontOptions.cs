using Babesiosis.Core.Models.Domain;
using System;
using System.Collections.Generic;
using System.Drawing;
using System.Text;

namespace Babesiosis.Core.Excel
{
  public class FontOptions
  {
    public string FontName { get; set; } = Guid.NewGuid().ToString();
    public Color FontColor { get; set; } = Color.Black;
    public bool IsBold { get; set; }
    public bool IsItalic { get; set; }
    public int Size { get; set; } = 10;
  }
}
