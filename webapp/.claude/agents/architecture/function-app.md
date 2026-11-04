# API LAYER (AZURE FUNCTION APPS) 

## Overview
The API layer consists of lightweight Azure Function Apps that act as a routing layer between the Angular front-end and the C# back-end business logic.

## Core Responsibilities
- Receive HTTP requests from the Angular front-end
- Route requests to appropriate controllers in DataManager.Core.Api
- Return responses to the front-end
- Minimal logic - delegation only

## Project Structure
- **Project Name**: DataManager.Core.Functions
- **Source root**: nested one level — `DataManager.Core.Functions/Core.Functions/`
- **Organization**: `[Feature]/[SubFeature]/` — e.g. `Teams/Users/`, `Teams/Roles/`, `Manage/`
- **Pattern**: one class per function, one function per file
- **Shared base classes** (in `Core.Functions/`): `HttpFunctionBase.cs`,
  `ServiceBusFunctionBase.cs`, `FunctionBase.cs`, `ServerErrorResult.cs`, `ErrorResponse.cs`
- **Existing feature folders**: Auth, Custom, Emails, Lookup,
  Manage, Pipelines, Reference, Search, Setup, Teams

## Implementation Requirements

### Function App Structure
Functions derive from `HttpFunctionBase` and wrap their body in `ExecuteRequest`, which
handles JWT validation, logging, and exception→HTTP mapping. `GetUserId(req)` yields the
caller's user id for the controller call.

```csharp
public class GetUsers : HttpFunctionBase
{
  const string NAME = "teams-users-get";
  private readonly GetUsersController _controller;

  public GetUsers(IAppSettingsService appSettingsService,
    IJwtTokenGenerator tokenProvider,
    ILogger<GetUsers> logger,
    GetUsersController controller)
  : base(appSettingsService, tokenProvider, logger)
  {
    _controller = controller;
  }

  [Function(NAME)]
  [RequiredPermission(TeamsPermissions.UserReadId)]   // planned permission architecture
  public async Task<IActionResult> Run(
    [HttpTrigger(AuthorizationLevel.Function, "post", Route = NAME)] HttpRequest req)
  {
    return await ExecuteRequest(req, async (req) =>
    {
      string requestBody = await new StreamReader(req.Body).ReadToEndAsync();
      var command = JsonConvert.DeserializeObject<GetUsersCommand>(requestBody);
      var result = await _controller.HandleCommand(GetUserId(req), command);
      return new OkObjectResult(result);
    }, "Failed to get users");
  }
}
```

NOTE: `[RequiredPermission(...)]` and the `*Permissions` config classes are the **target**
permission architecture, not yet present in the codebase. Functions currently in the repo
enforce permissions inside the controller via `IUserPermissionsService.Assert(...)`.

### Dependency Injection
- Register all required services and controllers in `DataManager.Core.Functions/Program.cs`
  (isolated worker — there is no `Startup.cs`)
- Inject controllers and services via constructor injection
- Follow the service registration pattern established in existing function apps

### Naming Conventions
- Follow existing naming conventions from the Users feature
- Route names should be RESTful and consistent

### Request/Response Flow
1. Front-end sends HTTP request to Azure Function
2. Function extracts and validates request parameters
3. Function calls the appropriate controller method in DataManager.Core.Api
4. Controller executes business logic and returns result
5. Function returns response to front-end
