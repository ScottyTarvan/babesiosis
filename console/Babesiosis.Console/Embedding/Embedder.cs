using System.ClientModel;
using Azure.AI.OpenAI;
using OpenAI.Embeddings;

namespace Babesiosis.Console.Embedding
{
  /// <summary>
  /// Generates embeddings with an Azure OpenAI deployment. The SDK retries throttled (429)
  /// and transient failures with back-off before an exception reaches the caller.
  /// </summary>
  internal sealed class Embedder
  {
    private readonly EmbeddingClient _client;
    private readonly int _dimensions;

    public Embedder(string endpoint, string apiKey, string deployment, int dimensions)
    {
      var azure = new AzureOpenAIClient(new Uri(endpoint), new ApiKeyCredential(apiKey));
      _client = azure.GetEmbeddingClient(deployment);
      _dimensions = dimensions;
    }

    /// <summary>Returns one vector per input, in input order.</summary>
    public async Task<float[][]> EmbedAsync(IReadOnlyList<string> inputs, CancellationToken cancellationToken)
    {
      var options = new EmbeddingGenerationOptions { Dimensions = _dimensions };
      OpenAIEmbeddingCollection result = await _client.GenerateEmbeddingsAsync(inputs, options, cancellationToken);

      var vectors = new float[inputs.Count][];
      foreach (var embedding in result)
      {
        var vector = embedding.ToFloats().ToArray();
        if (vector.Length != _dimensions)
          throw new InvalidOperationException(
            $"The deployment returned {vector.Length} dimensions; the article.embedding column expects {_dimensions}.");
        vectors[embedding.Index] = vector;
      }

      if (vectors.Any(v => v is null))
        throw new InvalidOperationException("The embedding response did not contain a vector for every input.");

      return vectors;
    }
  }
}
