import { MockRegistration } from 'app/_mocks/mock-handler';
import { articlesAgentAskMock } from 'app/_mocks/handlers/articles-agent-ask.mock';
import { articlesListGetMock } from 'app/_mocks/handlers/articles-list-get.mock';
import { authPasswordLoginMock } from 'app/_mocks/handlers/auth-password-login.mock';
import { authPasswordForgotMock } from 'app/_mocks/handlers/auth-password-forgot.mock';
import { authPasswordResetMock } from 'app/_mocks/handlers/auth-password-reset.mock';
import { authSsoExchangeMock } from 'app/_mocks/handlers/auth-sso-exchange.mock';
import {
  platformMcpTokensCreateMock,
  platformMcpTokensRevokeMock,
  platformMcpTokensSearchMock,
} from 'app/_mocks/handlers/platform-mcp-tokens.mock';
import { jobsBackgroundGetMock } from 'app/_mocks/handlers/jobs-background-get.mock';
import { reviewCategoryYearCountsGetMock } from 'app/_mocks/handlers/review-category-year-counts-get.mock';
import { reviewListGetMock } from 'app/_mocks/handlers/review-list-get.mock';

/**
 * Central mock registry. Add new endpoint mocks here as you encounter
 * screens that need them. The interceptor warns in the console with the
 * exact file path to create whenever an un-mocked endpoint is called.
 *
 * Ordering: authPasswordLoginMock first (it's the entry point), then all other
 * handlers alphabetically by route.
 */
export const mockRegistrations: MockRegistration[] = [
  authPasswordLoginMock,
  articlesAgentAskMock,
  articlesListGetMock,
  authPasswordForgotMock,
  authPasswordResetMock,
  authSsoExchangeMock,
  // The topbar bell's feed. Walks a scripted sequence rather than returning a
  // fixed payload — see the handler for why.
  jobsBackgroundGetMock,
  platformMcpTokensSearchMock,
  platformMcpTokensCreateMock,
  platformMcpTokensRevokeMock,
  reviewCategoryYearCountsGetMock,
  reviewListGetMock,
];
