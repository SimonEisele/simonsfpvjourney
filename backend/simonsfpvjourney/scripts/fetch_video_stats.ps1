# Runs YouTube stats fetch. Requires YOUTUBE_API_KEY to be set in environment.
$ErrorActionPreference = 'Stop'

Set-Location 'C:\Github\private\simonsfpvjourney\backend\simonsfpvjourney'

if (-not $env:YOUTUBE_API_KEY -or $env:YOUTUBE_API_KEY -eq '') {
  Write-Error 'YOUTUBE_API_KEY not set';
  exit 1
}

"[FetchVideoStats] Starting at $(Get-Date)"
& '..\env\Scripts\python.exe' manage.py fetch_video_stats
"[FetchVideoStats] Finished at $(Get-Date)"