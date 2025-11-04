@echo off
REM run_all_cmd.bat — tworzy venv, instaluje deps, zrzuca PL+EN ALL do .\out
setlocal enabledelayedexpansion
cd /d %~dp0
python -m venv .venv
call .\.venv\Scripts\activate.bat
pip install -r requirements_wikical.txt
if not exist out mkdir out
python wikical_harvester_v2.py --both-langs --out-dir .\out
