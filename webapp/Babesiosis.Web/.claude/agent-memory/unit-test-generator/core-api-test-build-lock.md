---
name: core-api-test-build-lock
description: Babesiosis.Core.Api.Test CAN hit MSB3021/MSB3027 via Babesiosis.Mcp.Functions; dotnet test has no --no-dependencies, use -p:BuildProjectReferences=false
metadata:
  type: project
---

`dotnet test Babesiosis.Core.Api.Test/...` builds `Babesiosis.Mcp.Functions` as a dependency. When
Visual Studio / a Functions host holds `Babesiosis.Mcp.Functions/bin/Debug/net10.0/*.dll`, the build
fails with MSB3021/MSB3027 (copy of Babesiosis.DataFactory.dll) after 10 retries (~15 s).

**Why:** the lock is on the dependency's output, not on a compile error; the test project itself is fine.

**How to apply:** `dotnet test` rejects `--no-dependencies` (MSB1001). Re-run the same command with
`-p:BuildProjectReferences=false` (no `--no-build`): it compiles the test project against the
dependency DLLs the first run already built. Do the first full run anyway so Core.Api is fresh.
The older note in the main memory that Core.Api.Test is "never affected" is out of date.
Repo root is `C:\Workspaces\Babesiosis` (not `Babesiosis.Web`); `tasks/` and `.claude/specs/working/`
live there.
