[CmdletBinding()]
param(
    [switch]$SkipBrowser
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$siteRoot = Join-Path $repoRoot 'docs'
$userProfile = [Environment]::GetFolderPath('UserProfile')
$workspaceHome = Split-Path -Parent (Split-Path -Parent $repoRoot)
$runtimeRoots = @($userProfile, $HOME, $env:USERPROFILE, $workspaceHome) |
    Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
    Select-Object -Unique |
    ForEach-Object {
        Join-Path $_ '.cache\codex-runtimes\codex-primary-runtime\dependencies'
    }
$bundledPython = @($runtimeRoots | ForEach-Object { Join-Path $_ 'python\python.exe' })
$bundledNode = @($runtimeRoots | ForEach-Object { Join-Path $_ 'node\bin\node.exe' })

function Resolve-Runtime {
    param(
        [Parameter(Mandatory)] [string]$Label,
        [Parameter(Mandatory)] [string[]]$CommandNames,
        [Parameter(Mandatory)] [string[]]$BundledPaths,
        [Parameter(Mandatory)] [string[]]$ProbeArguments
    )

    $candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($bundledPath in $BundledPaths) {
        if (Test-Path -LiteralPath $bundledPath -PathType Leaf) {
            $candidates.Add($bundledPath)
        }
    }
    foreach ($commandName in $CommandNames) {
        $command = Get-Command $commandName -CommandType Application -ErrorAction SilentlyContinue |
            Select-Object -First 1
        if ($null -ne $command) {
            $candidates.Add($command.Source)
        }
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        try {
            & $candidate @ProbeArguments *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        } catch {
            continue
        }
    }
    throw "$Label runtime was not found on PATH or at: $($BundledPaths -join ', ')"
}

function Invoke-NativeStep {
    param(
        [Parameter(Mandatory)] [string]$Label,
        [Parameter(Mandatory)] [string]$FilePath,
        [Parameter(Mandatory)] [string[]]$ArgumentList
    )

    Write-Host "==> $Label"
    & $FilePath @ArgumentList
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode"
    }
}

$python = Resolve-Runtime -Label 'Python' -CommandNames @('python', 'python3') `
    -BundledPaths $bundledPython -ProbeArguments @('--version')
$node = $null
if (-not $SkipBrowser) {
    $node = Resolve-Runtime -Label 'Node.js' -CommandNames @('node') `
        -BundledPaths $bundledNode -ProbeArguments @('--version')
}

$oldPythonUtf8 = $env:PYTHONUTF8
$oldPythonPath = $env:PYTHONPATH
$oldNodePath = $env:NODE_PATH
$pathSeparator = [IO.Path]::PathSeparator

try {
    $env:PYTHONUTF8 = '1'
    $env:PYTHONPATH = (@($PSScriptRoot, $oldPythonPath) |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) }) -join $pathSeparator

    $nodeModuleCandidates = @(
        $runtimeRoots | ForEach-Object {
            Join-Path $_ 'node\node_modules'
            Join-Path $_ 'node\node_modules\.pnpm\node_modules'
        }
        $oldNodePath
    ) | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    $env:NODE_PATH = ($nodeModuleCandidates | Select-Object -Unique) -join $pathSeparator

    Push-Location $repoRoot
    try {
        $pythonFiles = @(
            (Join-Path $PSScriptRoot 'build_season2.py'),
            (Join-Path $PSScriptRoot 'season2_config.py'),
            (Join-Path $PSScriptRoot 'test_season2_pages.py'),
            (Join-Path $PSScriptRoot 'test_law_page.py'),
            (Join-Path $PSScriptRoot 'test_site_publication.py')
        )
        $compileCode = @'
import pathlib, sys
for value in sys.argv[1:]:
    path = pathlib.Path(value)
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
'@
        $compileArguments = @('-I', '-c', $compileCode) + $pythonFiles
        Invoke-NativeStep -Label 'Compile Python sources in memory' -FilePath $python `
            -ArgumentList $compileArguments
        Invoke-NativeStep -Label 'Rebuild Season 2 pages' -FilePath $python `
            -ArgumentList @('-B', (Join-Path $PSScriptRoot 'build_season2.py'), '--output-dir', $siteRoot)
        Invoke-NativeStep -Label 'Run Season 2 regression tests' -FilePath $python `
            -ArgumentList @('-B', '-m', 'unittest', 'tools.test_season2_pages', '-v')
        Invoke-NativeStep -Label 'Run Law regression tests' -FilePath $python `
            -ArgumentList @('-B', '-m', 'unittest', 'tools.test_law_page', '-v')
        Invoke-NativeStep -Label 'Run site publication tests' -FilePath $python `
            -ArgumentList @('-B', '-m', 'unittest', 'tools.test_site_publication', '-v')

        if ($SkipBrowser) {
            Write-Host '==> Skip browser QA (-SkipBrowser)'
        } else {
            Invoke-NativeStep -Label 'Run 360-state browser QA' -FilePath $node `
                -ArgumentList @((Join-Path $PSScriptRoot 'validate_season2.mjs'))
        }
    } finally {
        Pop-Location
    }
} finally {
    $env:PYTHONUTF8 = $oldPythonUtf8
    $env:PYTHONPATH = $oldPythonPath
    $env:NODE_PATH = $oldNodePath
}
