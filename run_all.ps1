# run_all.ps1 — tworzy venv, instaluje deps, zrzuca PL+EN ALL do .\out
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

cd $PSScriptRoot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements_wikical.txt

New-Item -ItemType Directory -Path .\out -Force | Out-Null

python .\wikical_harvester_v2.py --both-langs --out-dir .\out
