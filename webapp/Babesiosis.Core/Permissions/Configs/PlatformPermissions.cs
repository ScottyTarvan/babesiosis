using System;

namespace Babesiosis.Core.Permissions.Configs
{
  /// <summary>
  /// Permissions for the Platform area — capabilities that span the entire
  /// system and are not dataset/setup/manage/reports specific. Currently:
  /// MCP (Model Context Protocol) server access for programmatic data access.
  /// </summary>
  public static class PlatformPermissions
  {
    const string PLATFORM = "platform";
    const string MCP_ACCESS = "mcp-access";

    //************************************************
    //MCP ACCESS
    //************************************************
    // Creating a personal access token for MCP server connections. Searching
    // and revoking tokens are authenticated operations that do not require
    // this explicit permission.
    public const string McpAccessId = "{7D8A1B2C-F9E4-4D3A-A5C6-B9E2D3F4A8C7}";
    public static PermissionItem McpAccess => new PermissionItem
    {
      Id = Guid.Parse(McpAccessId),
      Category = PLATFORM,
      Group = MCP_ACCESS,
      Action = PermissionAction.Add
    };
  }
}
