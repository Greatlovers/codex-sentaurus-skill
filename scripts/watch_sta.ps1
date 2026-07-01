param(
  [Parameter(Mandatory=$true)][string]$HostName,
  [Parameter(Mandatory=$true)][string]$RemoteProject,
  [Parameter(Mandatory=$true)][string]$StaFile,
  [int]$IntervalSeconds = 300,
  [string]$OutDir = ".",
  [string]$RunId = "",
  [string]$SubmittedAt = "",
  [string]$Node = "",
  [switch]$Once
)

$ErrorActionPreference = "Stop"

if ($IntervalSeconds -lt 1) {
  throw "IntervalSeconds must be at least 1."
}

if (-not $RunId) {
  $RunId = "watch_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + ([guid]::NewGuid().ToString("N").Substring(0, 8))
}

$watcherStartedAt = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$statusJson = Join-Path $OutDir "sentaurus-sta-watch.json"
$terminalJson = Join-Path $OutDir "sentaurus-sta-terminal.json"
$terminalTxt = Join-Path $OutDir "sentaurus-sta-terminal.txt"

function ConvertTo-RemoteSingleQuoted {
  param([string]$Value)
  return "'" + ($Value -replace "'", "'\''") + "'"
}

function Get-StaStatus {
  param([string[]]$Lines)

  foreach ($line in $Lines) {
    if ($line -match "\|") {
      $parts = $line -split "\|"
      if ($parts.Length -ge 3) {
        return $parts[2].Trim().ToLowerInvariant()
      }
    }
  }

  return ""
}

function Read-RemoteSta {
  $project = ConvertTo-RemoteSingleQuoted $RemoteProject
  $sta = ConvertTo-RemoteSingleQuoted $StaFile
  $remoteCommand = "cd $project && cat $sta 2>/dev/null || true"
  & ssh $HostName $remoteCommand
}

while ($true) {
  $now = Get-Date

  try {
    $raw = @(Read-RemoteSta)
    $status = Get-StaStatus $raw
    $payload = [ordered]@{
      generated_at = $now.ToString("yyyy-MM-ddTHH:mm:ssK")
      run_id = $RunId
      watcher_started_at = $watcherStartedAt
      submitted_at = $SubmittedAt
      host = $HostName
      project = $RemoteProject
      sta_file = $StaFile
      node = $Node
      status = $status
      raw_sta = ($raw -join "`n")
    }

    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statusJson -Encoding UTF8

    if ($status -and $status -notin @("queued", "running")) {
      $marker = [ordered]@{
        generated_at = $now.ToString("yyyy-MM-ddTHH:mm:ssK")
        run_id = $RunId
        watcher_started_at = $watcherStartedAt
        submitted_at = $SubmittedAt
        host = $HostName
        project = $RemoteProject
        sta_file = $StaFile
        node = $Node
        status = $status
        raw_sta = ($raw -join "`n")
        status_file = $statusJson
      }

      $marker | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $terminalJson -Encoding UTF8
      "terminal status: $status`nstatus file: $statusJson" | Set-Content -LiteralPath $terminalTxt -Encoding UTF8
      exit 0
    }
  } catch {
    $payload = [ordered]@{
      generated_at = $now.ToString("yyyy-MM-ddTHH:mm:ssK")
      run_id = $RunId
      watcher_started_at = $watcherStartedAt
      submitted_at = $SubmittedAt
      host = $HostName
      project = $RemoteProject
      sta_file = $StaFile
      node = $Node
      status = "ssh_error"
      error = $_.Exception.Message
    }

    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statusJson -Encoding UTF8
    if ($Once) {
      exit 2
    }
  }

  if ($Once) {
    exit 0
  }

  Start-Sleep -Seconds $IntervalSeconds
}

