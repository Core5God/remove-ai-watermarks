$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# This runs on a Windows x64 machine or the GitHub Actions Windows runner.
py -3.11 -m venv .build-venv
& .\.build-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.build-venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.build-venv\Scripts\python.exe -m unittest discover -s tests -v

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
& .\.build-venv\Scripts\pyinstaller.exe --noconfirm --clean --windowed --name "WatermarkHelper" --add-data "static;static" --collect-all remove_ai_watermarks launcher.py

# Start the actual frozen Windows executable and require its homepage to load.
$env:WATERMARK_HELPER_PORT = "17860"
$env:WATERMARK_HELPER_NO_BROWSER = "1"
$smokeProcess = Start-Process -FilePath ".\dist\WatermarkHelper\WatermarkHelper.exe" -PassThru
$homepageOk = $false
try {
  for ($attempt = 0; $attempt -lt 30; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
      $response = Invoke-WebRequest -UseBasicParsing -Uri "http://127.0.0.1:17860/" -TimeoutSec 2
      if ($response.StatusCode -eq 200 -and $response.Content -match "水印清除助手") {
        $homepageOk = $true
        break
      }
    } catch { }
  }
  if (-not $homepageOk) { throw "打包后的 Windows 程序首页未能正常打开" }
  Write-Host "Frozen executable homepage smoke test passed"
} finally {
  if ($smokeProcess -and -not $smokeProcess.HasExited) { Stop-Process -Id $smokeProcess.Id -Force }
}

$isccCandidates = @(
  "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
  "C:\Program Files\Inno Setup 6\ISCC.exe",
  "C:\ProgramData\chocolatey\lib\innosetup\tools\ISCC.exe"
)
$iscc = $isccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not (Test-Path $iscc)) { throw "找不到 Inno Setup 编译器 ISCC.exe" }
& $iscc installer\setup.iss
