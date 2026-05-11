# install-speckit.ps1
#
# Sets up SpecKit lean commands for Claude Code.
# Unzip speckit-setup.zip into your project root, then run this script.
#
# Usage:
#   .\speckit-setup\install-speckit.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Always install into the folder ABOVE this script (the project root)
$root = Split-Path -Parent $scriptDir

Write-Host ""
Write-Host "SpecKit Setup" -ForegroundColor Cyan
Write-Host "Installing into: $root"
Write-Host ""

$files = @(
    "speckit.constitution.md",
    "speckit.specify.md",
    "speckit.plan.md",
    "speckit.tasks.md",
    "speckit.implement.md"
)

$sourceDir = Join-Path $scriptDir ".claude\commands"
$targetDir = Join-Path $root ".claude\commands"

New-Item -ItemType Directory -Force -Path $targetDir              | Out-Null
New-Item -ItemType Directory -Force -Path "$root\.specify\memory" | Out-Null

# Copy the 5 command files
$ok = $true
foreach ($file in $files) {
    $src = Join-Path $sourceDir $file
    $dst = Join-Path $targetDir $file
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  OK  $file" -ForegroundColor Green
    } else {
        Write-Host "  ERR $file not found in $sourceDir" -ForegroundColor Red
        $ok = $false
    }
}

# Add SpecKit section to CLAUDE.md if not already present
$claudeMd = Join-Path $root "CLAUDE.md"
$section = @"


<!-- SPECKIT START -->
## SpecKit Workflow

Use these slash commands in Claude Code for spec-driven development:

| Command | Creates | Description |
|---------|---------|-------------|
| ``/speckit.constitution`` | ``.specify/memory/constitution.md`` | Project principles and rules |
| ``/speckit.specify`` | ``specs/<feature>/spec.md`` | Requirements and scenarios |
| ``/speckit.plan`` | ``specs/<feature>/plan.md`` | Technical implementation plan |
| ``/speckit.tasks`` | ``specs/<feature>/tasks.md`` | Ordered task checklist |
| ``/speckit.implement`` | code | Executes all tasks in order |

**Workflow:** constitution -> specify -> plan -> tasks -> implement
<!-- SPECKIT END -->
"@

if (Test-Path $claudeMd) {
    $content = Get-Content $claudeMd -Raw
    if ($content -notmatch "SPECKIT START") {
        Add-Content $claudeMd $section -Encoding UTF8
        Write-Host "  OK  SpecKit section added to existing CLAUDE.md" -ForegroundColor Green
    } else {
        Write-Host "  --  CLAUDE.md already has SpecKit section" -ForegroundColor Yellow
    }
} else {
    $section.TrimStart() | Set-Content $claudeMd -Encoding UTF8
    Write-Host "  OK  CLAUDE.md created" -ForegroundColor Green
}

Write-Host ""
if ($ok) {
    Write-Host "Done! Open Claude Code in this folder and start with:" -ForegroundColor Green
    Write-Host "  $root" -ForegroundColor White
    Write-Host ""
    Write-Host "  /speckit.constitution  <- start here" -ForegroundColor Cyan
    Write-Host "  /speckit.specify"
    Write-Host "  /speckit.plan"
    Write-Host "  /speckit.tasks"
    Write-Host "  /speckit.implement"
} else {
    Write-Host "Something went wrong - see manual installation in README.md" -ForegroundColor Red
}
Write-Host ""
