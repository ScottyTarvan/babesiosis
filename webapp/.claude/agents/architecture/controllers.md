# BACK-END (C# CONTROLLERS) 

## PROJECT CONTEXT
- Project: DataManager.Core.Api
- Purpose: Business logic layer that orchestrates services
- Pattern: Controller → Service → Repository

## PRIMARY RESPONSIBILITIES
1. Handle all business logic 
2. Orchestrate calls to multiple services from DataManager.Core library
3. Transform business models to/from view models
4. Coordinate database operations through DbContext

## FOLDER STRUCTURE (STRICT)

Source is nested one level under the project folder — `DataManager.Core.Api/Core.Api/…`.

```
DataManager.Core.Api/Core.Api/[Feature]/
├── [Feature]DbContext.cs                 # e.g. TeamsDbContext, AuthDbContext
└── [SubFeature]/                         # e.g. Teams/Users, Teams/Roles
    ├── Controllers/
    │   └── [Op][Entity]Controller.cs     # one class per operation
    ├── ViewModels/
    │   └── [Entity]ViewModel.cs
    ├── Commands/
    │   └── [Op][Entity]Command.cs
    └── Mapping/
        └── [SubFeature]Profile.cs
```

Canonical reference: `DataManager.Core.Api/Core.Api/Teams/Users/`.
Existing feature folders: Auth, Lookup, Manage, Pipelines,
Reference, Search, Setup, Teams.

## IMPLEMENTATION SEQUENCE (FOLLOW STRICTLY)
1. Create view model classes (use classes, NOT interfaces)
2. Create command classes for operations
3. Create feature-specific DbContext class in root feature folder
4. Create AutoMapper mapping profile in Mapping folder
5. Implement controller with dependency injection
6. Add proper error handling and validation
7. Implement authorization checks

## CONTROLLER IMPLEMENTATION GUIDELINES

A "controller" here is NOT an ASP.NET MVC/WebAPI controller. It is a plain C# class with
a single public `HandleCommand(Guid userId, TCommand command)` method. It never returns
`IActionResult` — it returns a view model and lets exceptions bubble to the function layer,
which maps them to HTTP results.

### Dependency Injection
```csharp
// Always inject required services in constructor
private readonly IDbContextService _dbContextService;
private readonly IUserPermissionsService _permissionsService;
private readonly IMapper _mapper;

public GetUsersController(
    IDbContextService dbContextService,
    IUserPermissionsService permissionsService,
    IMapper mapper)
{
    _dbContextService = dbContextService;
    _permissionsService = permissionsService;
    _mapper = mapper;
}

public async Task<UsersViewModel> HandleCommand(Guid userId, GetUsersCommand command)
{
    _permissionsService.Assert(userId, "read", "teams-user");

    using var dbContext = _dbContextService.CreateDbContext<TeamsDbContext>();
    ...
}
```

### Naming Conventions
- Follow existing Users feature patterns exactly
  (`DataManager.Core.Api/Core.Api/Teams/Users/`)
- Controllers: [Op][Entity]Controller.cs — `GetUsersController`, `AddUserController`,
  `EditUserController`, `DeleteUserController`. One operation per class.
- Method: always `HandleCommand`
- ViewModels: [Entity]ViewModel, [Entity]sViewModel (list wrapper)
- Commands: [Op][Entity]Command, or the shared `SearchCommand` from `DataManager.Core/Commands/`

### Error Handling Pattern
Do not catch-and-convert inside the controller. Assert preconditions and throw; the
`HttpFunctionBase.ExecuteRequest` wrapper in the function app handles logging and the
HTTP response mapping.

```csharp
_permissionsService.Assert(userId, "edit", "teams-user");
Assert.NotNull(command.User, "User is required");
```

### View Model Usage
- Use AutoMapper for model transformations
- Keep view models in dedicated ViewModels subfolder
- Use classes (not interfaces) for all DTOs

### DbContext Usage
- Create feature-specific DbContext class in root feature folder
- Inject IDbContextService through constructor
- Use async methods: ToListAsync(), FirstOrDefaultAsync(), SaveChangesAsync()

