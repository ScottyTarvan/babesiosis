using System.Text.Json;

namespace Babesiosis.Core.Extensions
{
  public static class DeserializeExtensions
  {
    private static JsonSerializerOptions defaultSerializerOptions = new JsonSerializerOptions()
    {
      PropertyNameCaseInsensitive = true
    };

    public static T Deserialize<T>(this string json)
    {
      return Deserialize<T>(json, defaultSerializerOptions);
    }

    public static T Deserialize<T>(this string json, JsonSerializerOptions settings)
    {
      return JsonSerializer.Deserialize<T>(json, settings);
    }
  }
}
