@echo off
setlocal
title GroveCast OBS
cd /d "%~dp0"
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY where python3 >nul 2>&1 && set "PY=python3"
if not defined PY where py >nul 2>&1 && set "PY=py -2"
if not defined PY (
  echo Need Python for the OBS page.
  pause
  exit /b 1
)
echo OBS Browser Source:  http://127.0.0.1:8099/obs
%PY% "%~dp0serve.py"
pause
endlocal
