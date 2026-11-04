import { LoadOptions } from 'app/core/commands/search.command';

/** Mirrors `GetArticleListCommand`: the grid's skip, take and sort. */
export interface GetArticleListCommand {
  loadOptions?: LoadOptions;
}
