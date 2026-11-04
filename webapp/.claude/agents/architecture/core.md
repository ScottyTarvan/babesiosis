# LIBRARY (CORE CODE) 

## Project Purpose
DataManager.Core is the foundational library layer containing reusable code, services, and business models shared across the application.

## Folder Structure

### Services (Services/ folder)
- Contains service interfaces and implementations
- Services encapsulate reusable business logic
- Follow dependency injection pattern
- Name convention: I{ServiceName}Service (interface), {ServiceName}Service (implementation)
- Register services in the function app services container during dependency injection setup

### Models (Models/ folder)
- Contains business domain models (entities)
- These are the core data structures representing business concepts
- Grouped into area sub-folders: `Models/Auth/`, `Models/Charts/`, `Models/Domain/`,
  `Models/Email/`, `Models/Events/`, `Models/Meta/`, `Models/Pipelines/`, `Models/Teams/`,
  `Models/Workflows/`

### Entity Framework Configurations (Data/Configs/ folder)
- Contains Fluent API configurations for EF Core entities
- Each entity should have its own configuration class
- Mirrors the Models area sub-folders: `Data/Configs/Auth/`, `Data/Configs/Meta/`,
  `Data/Configs/Pipelines/`, `Data/Configs/Reference/`, `Data/Configs/Teams/`,
  `Data/Configs/Workflows/`
- Name convention: {EntityName}Config (e.g. `Data/Configs/Teams/PermissionConfig.cs`)
- `Data/DbContextBase.cs` holds the shared DbSets that every feature DbContext inherits

## Implementation Guidelines

### When Creating New Services
1. Define interface first (I{ServiceName}Service)
2. Implement interface in concrete class ({ServiceName}Service)
3. Add service registration to DI container
4. Inject dependencies through constructor

### When Creating EF Configurations
1. One configuration class per entity
2. Configure all relationships explicitly

## Important Notes
- This library has NO dependencies on API, Functions, or Web projects
