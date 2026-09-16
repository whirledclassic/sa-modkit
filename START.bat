@echo off
setlocal EnableExtensions
title SA Modkit
color 0A
cd /d "%~dp0"

echo.
echo   SA MODKIT  -  Windows 7 / 8 / 10 / 11
echo   Pick the GTA San Andreas folder, tick packs, Install.
echo.

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY where python3 >nul 2>&1 && set "PY=python3"
if not defined PY where py >nul 2>&1 && set "PY=py -2"

if not defined PY (
  echo Python was not found.
  echo Windows 7: install Python 2.7.18 or 3.8.10 from python.org
  echo Windows 10/11: install Python 3.8 or newer and tick Add python.exe to PATH
  pause
  exit /b 1
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
echo Launching GUI...
%PY% "%~dp0grovekit\app.py"
if errorlevel 1 (
  echo GUI failed. Falling back to folder dialog + CLI.
  %PY% -m grovekit.cli --browse --all
  pause
)
endlocal
