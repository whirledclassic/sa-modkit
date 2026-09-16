@echo off
setlocal EnableExtensions
title SA Modkit
color 0A
cd /d "%~dp0"

echo.
echo   SA MODKIT  -  Windows 7 / 8 / 10 / 11
echo   Tick only the packs you want. Unticked packs stay off the game.
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
  echo.
  echo CLI without a GUI:
  echo   python -m grovekit.cli --browse
  pause
  exit /b 1
)

set "PYTHONPATH=%CD%;%PYTHONPATH%"
echo Launching GUI...
%PY% "%~dp0grovekit\app.py"
if errorlevel 1 (
  echo GUI failed. Folder dialog, then you type which packs.
  echo It will NOT install everything by default.
  %PY% -m grovekit.cli --browse
  pause
)
endlocal
