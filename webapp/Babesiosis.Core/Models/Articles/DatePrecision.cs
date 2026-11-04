namespace Babesiosis.Core.Models.Articles
{
  /// <summary>
  /// How much of article.pub_date is known. The date is stored as the first day of the
  /// period, so a Year value of 2019-01-01 means "some time in 2019".
  /// Stored as the single character in article.pub_date_precision (CK_article_pub_date_precision).
  /// </summary>
  public enum DatePrecision
  {
    Year = 'Y',
    Month = 'M',
    Day = 'D'
  }
}
