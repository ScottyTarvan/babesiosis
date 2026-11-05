<#
.SYNOPSIS
    Sets up plain-text semantic search in babesiosis-db.

.DESCRIPTION
    Runs semantic-search-setup.sql (REST endpoint switch, master key, API-key credential,
    external model, smoke test), then semantic-search.sql (dbo.search_articles) and
    passage-search.sql (dbo.search_passages).

    The endpoint, deployment and key come from appsettings.Local.json and reach sqlcmd as
    environment variables, so the key is not written to a file or shown on a command line.
    You are prompted for a master key password only if the database has no master key yet.

    Run as a Windows login that is sysadmin on the instance. Re-run after regenerating the key.
#>
[CmdletBinding()]
param(
    [string] $Server = 'localhost',
    [string] $Database = 'babesiosis-db'
)

$ErrorActionPreference = 'Stop'
$projectDir = Split-Path -Parent $PSScriptRoot
$settings = Get-Content (Join-Path $projectDir 'appsettings.json') -Raw | ConvertFrom-Json
$localPath = Join-Path $projectDir 'appsettings.Local.json'
if (-not (Test-Path $localPath)) { throw "Missing $localPath (copy appsettings.Local.example.json)." }
$local = Get-Content $localPath -Raw | ConvertFrom-Json

$endpoint = [string]$local.AzureOpenAI.Endpoint
$deployment = [string]$local.AzureOpenAI.Deployment
$apiKey = [string]$local.AzureOpenAI.ApiKey
if (-not $endpoint -or -not $deployment -or -not $apiKey) {
    throw 'AzureOpenAI Endpoint, Deployment and ApiKey must all be set in appsettings.Local.json.'
}
if (-not $endpoint.EndsWith('/')) { $endpoint += '/' }

$sqlcmdArgs = @('-S', $Server, '-d', $Database, '-E', '-C', '-b')

function Invoke-SqlcmdChecked([string[]] $extraArgs) {
    & sqlcmd @sqlcmdArgs @extraArgs
    if ($LASTEXITCODE -ne 0) { throw "sqlcmd failed with exit code $LASTEXITCODE." }
}

$hasMasterKey = & sqlcmd @sqlcmdArgs -h -1 -W -Q "SET NOCOUNT ON; SELECT COUNT(*) FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##';"
if ($LASTEXITCODE -ne 0) { throw "Could not connect to $Server/$Database." }

$masterKeyPassword = 'unused'
if ((($hasMasterKey | Select-Object -First 1) -as [string]).Trim() -eq '0') {
    Write-Host "The database has no master key. Choose a password for it and keep it somewhere safe;"
    Write-Host "you need it to restore the database (and its stored API key) on another server."
    $first = Read-Host -AsSecureString 'Master key password'
    $second = Read-Host -AsSecureString 'Confirm password'
    $toPlain = { param($s) [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($s)) }
    $masterKeyPassword = & $toPlain $first
    if ($masterKeyPassword -ne (& $toPlain $second)) { throw 'Passwords do not match.' }
}

$variables = @{
    BABESIOSIS_AOAI_ENDPOINT        = $endpoint
    BABESIOSIS_AOAI_DEPLOYMENT      = $deployment
    BABESIOSIS_AOAI_KEY             = $apiKey.Replace("'", "''")
    BABESIOSIS_EMBEDDING_MODEL      = [string]$settings.Embedding.Model
    BABESIOSIS_EMBEDDING_DIMENSIONS = [string]$settings.Embedding.Dimensions
    BABESIOSIS_MASTER_KEY_PASSWORD  = $masterKeyPassword.Replace("'", "''")
}

try {
    foreach ($name in $variables.Keys) { Set-Item "env:$name" $variables[$name] }
    Invoke-SqlcmdChecked @('-i', (Join-Path $PSScriptRoot 'semantic-search-setup.sql'))
    Invoke-SqlcmdChecked @('-i', (Join-Path $PSScriptRoot 'semantic-search.sql'))
    Invoke-SqlcmdChecked @('-i', (Join-Path $PSScriptRoot 'passage-search.sql'))
    Write-Host 'Semantic search is ready: EXEC dbo.search_articles @question = N''...''; EXEC dbo.search_passages @question = N''...'';'
}
finally {
    foreach ($name in $variables.Keys) { Remove-Item "env:$name" -ErrorAction SilentlyContinue }
}
