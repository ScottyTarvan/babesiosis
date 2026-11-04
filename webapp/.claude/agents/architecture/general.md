# CONDENSED ARCHITECTURE GUIDE

## 4-LAYER STRUCTURE (One-way dependencies: Web → Functions → API → Core)

Layer 1: Angular (DataManager.Web)
- UI/client logic, flat feature folders, CLASSES for DTOs (never interfaces)
- Run `ng build` after changes

Layer 2: Functions (DataManager.Core.Functions)
- Routing ONLY, no business logic, register in Program.cs

Layer 3: Controllers (DataManager.Core.Api)
- Business logic, authorization, AutoMapper
- Feature folders: Controllers/, ViewModels/, Commands/, Mapping/, [Feature]DbContext.cs

Layer 4: Core (DataManager.Core)
- Reusable services/models, NO upper-layer dependencies
- 3-Class Pattern: IService (interface) → ServiceProvider (factory) → Service (implementation)

## FOLDER PATTERNS

NOTE: both backend projects nest their source under a folder repeating the project
name — `DataManager.Core.Api/Core.Api/…` and `DataManager.Core.Functions/Core.Functions/…`.
Always include that level when writing or locating files.

Angular: src/app/[area]/[Name]/[Name].{component,service,viewmodel,command}.ts
Functions: DataManager.Core.Functions/Core.Functions/[Feature]/[SubFeature]/[Name].cs
Controllers: DataManager.Core.Api/Core.Api/[Feature]/[SubFeature]/{Controllers,ViewModels,Commands,Mapping}/
Core: DataManager.Core/Services/{I[Name]Service,Providers/[Name]ServiceProvider,Impl/[Name]Service}, Models/[Area]/, Data/Configs/[Area]/

Existing feature areas — Core.Api: Auth, Lookup, Manage, Pipelines,
Reference, Search, Setup, Teams. Core.Functions mirrors these plus Custom and Emails.
