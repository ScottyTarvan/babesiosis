using System.ComponentModel;

namespace Babesiosis.Core.Excel.Styles
{
    public enum Direction : short
    {
        None = 0,
        [Description("Top")]
        Top = 1,
        [Description("Bottom")]
        Bottom = 2,
        [Description("Left")]
        Left = 3,
        [Description("Right")]
        Right = 4,
        [Description("Center")]
        Center = 5,
    }
}
