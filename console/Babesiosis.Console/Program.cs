using Out = System.Console;

namespace Babesiosis.Console
{
  internal class Program
  {
    static async Task<int> Main(string[] args)
    {
      LoaderOptions options;
      try
      {
        options = LoaderOptions.Parse(args);
      }
      catch (ArgumentException ex)
      {
        Out.Error.WriteLine(ex.Message);
        Out.Error.WriteLine();
        Out.Error.WriteLine(LoaderOptions.Usage);
        return 2;
      }

      if (options.ShowHelp)
      {
        Out.WriteLine(LoaderOptions.Usage);
        return 0;
      }

      using var cancellation = new CancellationTokenSource();
      Out.CancelKeyPress += (_, e) =>
      {
        e.Cancel = true;
        cancellation.Cancel();
      };

      try
      {
        var settings = LoaderSettings.Load();
        var result = 0;
        if (!options.DatasetsOnly)
        {
          result = await new ArticleLoader(settings, options).RunAsync(cancellation.Token);
          // Passages and terms attach to article rows, so they load after the articles; a failed article still leaves the others.
          result = Math.Max(result, await new SectionLoader(settings, options).RunAsync(cancellation.Token));
          result = Math.Max(result, await new TermLoader(settings, options).RunAsync(cancellation.Token));
        }
        // Datasets link to articles by code, and experiments resolve their variables through the datasets, so this order matters.
        result = Math.Max(result, await new DatasetLoader(settings, options).RunAsync(cancellation.Token));
        result = Math.Max(result, await new ExperimentLoader(settings, options).RunAsync(cancellation.Token));
        return result;
      }
      catch (OperationCanceledException)
      {
        Out.Error.WriteLine("Cancelled. Articles already saved stay in the database.");
        return 130;
      }
      catch (Exception ex)
      {
        Out.Error.WriteLine($"Error: {ex.Message}");
        return 1;
      }
    }
  }
}
