$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# This runs on a Windows x64 machine or the GitHub Actions Windows runner.
py -3.11 -m venv .build-venv
& .\.build-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.build-venv\Scripts\python.exe -m pip install -r requirements.txt

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
& .\.build-venv\Scripts\pyinstaller.exe --noconfirm --clean --windowed --name "水印清除助手" --add-data "static;static" --collect-all remove_ai_watermarks launcher.py

$iscc = Get-ChildItem -Path "C:\Program Files (x86)","C:\Program Files" -Filter "ISCC.exe" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName
if (-not (Test-Path $iscc)) { throw "找不到 Inno Setup 编译器 ISCC.exe" }
& $iscc installer\水印清除助手.iss
