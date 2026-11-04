using System.ComponentModel;

namespace Babesiosis.Core.Excel.Styles
{
    public enum Border : short
    {
        None = 0,
        [Description("Thin")]
        Thin = 1,
        [Description("Thick")]
        Thick = 2,
        [Description("Dashed")]
        Dashed = 3,
        [Description("Double")]
        Double = 4,
    }
}
