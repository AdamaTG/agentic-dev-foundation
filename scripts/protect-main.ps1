param(
  [string]$Repository = 'AdamaTG/agentic-dev-foundation',
  [string]$Branch = 'main',
  [switch]$Apply
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI gh is required: https://cli.github.com/' }
& gh auth status
if ($LASTEXITCODE -ne 0) { throw 'Authenticate with gh auth login' }
$checks = @('verify', 'gate-next-fastapi', 'gate-expo', 'gate-flutter')
$body = @{
 name = 'ADF protected main'
 target = 'branch'
 enforcement = 'active'
 conditions = @{ref_name = @{include = @("refs/heads/$Branch"); exclude = @()}}
 rules = @(
   @{type='pull_request'; parameters=@{required_approving_review_count=1;dismiss_stale_reviews_on_push=$true;require_code_owner_review=$false;require_last_push_approval=$false;required_review_thread_resolution=$true}},
   @{type='required_status_checks';parameters=@{strict_required_status_checks=$true;do_not_enforce_on_create=$false;required_status_checks=@($checks | ForEach-Object { @{context=$_} })}}
 )
} | ConvertTo-Json -Depth 15
Write-Host "Repository: $Repository"
Write-Host "Required checks: $($checks -join ', ')"
if (-not $Apply) { Write-Host 'DRY RUN: no remote change. Add -Apply only after all check runs have succeeded.'; Write-Output $body; exit 0 }
$tmp = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
try {
  [System.IO.File]::WriteAllText($tmp, $body, [System.Text.UTF8Encoding]::new($false))
  & gh api -X POST "repos/$Repository/rulesets" -H 'Accept: application/vnd.github+json' --input $tmp
} finally { Remove-Item $tmp -ErrorAction SilentlyContinue }
if ($LASTEXITCODE -ne 0) { throw 'Ruleset creation failed; check admin permissions, plan eligibility, and existing rulesets' }
