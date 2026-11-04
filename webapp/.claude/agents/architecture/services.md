# SERVICES (BACKEND) 

## Overview
The services layer contains reusable cross-cutting services that provide shared functionality across the application. 
Services encapsulate business logic, data access, and external integrations in a maintainable, testable manner.

## Three-Class Service Pattern

Every service consists of THREE classes that work together:

### 1. Service Interface (I{ServiceName}Service)
**Purpose**: Defines the contract for the service
**Location**: `DataManager.Core/Services/I{ServiceName}Service.cs`
**Guidelines**:
- Name convention: Interface name starts with 'I', ends with 'Service'
- Contains only method signatures (no implementation)
- Use async methods for I/O operations (return Task or Task<T>)
- Include XML documentation comments describing each method's purpose
- Define clear input parameters and return types
- Example:
```csharp
/// <summary>
/// Provides permission checking functionality for users
/// </summary>
public interface IUserPermissionsService
{
    /// <summary>
    /// Checks if a user has a specific permission
    /// </summary>
    /// <param name="userId">The user ID to check</param>
    /// <param name="permission">The permission to verify</param>
    /// <returns>True if user has permission, false otherwise</returns>
    Task<bool> HasPermissionAsync(int userId, string permission);
}
```

### 2. Service Provider (Factory Class)
**Purpose**: Acts as a factory for the dependency injection container
**Location**: `DataManager.Core/Services/Providers/{ServiceName}ServiceProvider.cs`
**Guidelines**:
- Name convention: {ServiceName}ServiceProvider
- Contains static GetService method that creates service instances
- Handles dependency resolution for the service
- Receives IServiceProvider as parameter to resolve dependencies
- Returns the interface type (not the concrete implementation)
- Example:
```csharp
public class UserPermissionsServiceProvider
{
    public static IUserPermissionsService GetService(IServiceProvider serviceProvider)
    {
        // Resolve any dependencies the service needs
        var dbContext = serviceProvider.GetRequiredService<ApplicationDbContext>();
        var logger = serviceProvider.GetRequiredService<ILogger<UserPermissionsService>>();
        
        // Create and return the service instance
        return new UserPermissionsService(dbContext, logger);
    }
}
```

### 3. Service Implementation
**Purpose**: Contains the actual business logic and implementation
**Location**: `DataManager.Core/Services/Impl/{ServiceName}Service.cs`
- Example:
```csharp
public class UserPermissionsService : IUserPermissionsService
{
    private readonly ApplicationDbContext _dbContext;
    private readonly ILogger<UserPermissionsService> _logger;

    public UserPermissionsService(
        ApplicationDbContext dbContext,
        ILogger<UserPermissionsService> logger)
    {
        _dbContext = dbContext ?? throw new ArgumentNullException(nameof(dbContext));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
    }

    public async Task<bool> HasPermissionAsync(int userId, string permission)
    {
        try
        {
            var userPermissions = await _dbContext.UserPermissions
                .Where(up => up.UserId == userId && up.Permission == permission)
                .AnyAsync();

            _logger.LogInformation("Permission check for user {UserId}: {Permission} = {Result}", 
                userId, permission, userPermissions);

            return userPermissions;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error checking permission for user {UserId}", userId);
            throw;
        }
    }
}
```

## Service Registration

### Location
Services are registered in the dependency injection container at:
**File**: `DataManager.Core.Functions/Program.cs`
**Section**: Service registration block (typically after builder creation)

### Registration Pattern
Use the ServiceDescriptor pattern with the provider's GetService method:
```csharp
builder.Services.Add(new ServiceDescriptor(
    typeof(IUserPermissionsService),           // Interface type
    UserPermissionsServiceProvider.GetService, // Factory method
    ServiceLifetime.Transient));           // Lifetime scope
```

### Service Lifetimes

**Default: Use Transient**
- Services should be registered as `ServiceLifetime.Transient` by default

### Registration Example Block
```csharp
// In Program.cs
var builder = FunctionsApplication.CreateBuilder(args);

// Register services
builder.Services.Add(new ServiceDescriptor(typeof(IUserPermissionsService), UserPermissionsServiceProvider.GetService, ServiceLifetime.Transient));
builder.Services.Add(new ServiceDescriptor(typeof(INotificationService), NotificationServiceProvider.GetService, ServiceLifetime.Transient));
builder.Services.Add(new ServiceDescriptor(typeof(ICacheService), CacheServiceProvider.GetService, ServiceLifetime.Singleton));
builder.Services.Add(new ServiceDescriptor(typeof(IEmailService), EmailServiceProvider.GetService, ServiceLifetime.Transient));
```
