@echo off
setlocal EnableExtensions
title SA Modkit
color 0A
cd /d "%~dp0"
echo.
echo   SA MODKIT  -  Windows 7 / 8 / 10 / 11
echo   Tick only the packs you want.
echo.
if exist "%~dp0SA-Modkit.exe" (
  echo Launching SA-Modkit.exe
  start "" "%~dp0SA-Modkit.exe"
  exit /b 0
)
echo No EXE yet. Building one with the built-in .NET compiler...
call "%~dp0BUILD_EXE.bat"
if exist "%~dp0SA-Modkit.exe" (
  start "" "%~dp0SA-Modkit.exe"
  exit /b 0
)
echo EXE build skipped. Trying Python GUI...
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"
if not defined PY where python3 >nul 2>&1 && set "PY=python3"
if not defined PY where py >nul 2>&1 && set "PY=py -2"
if not defined PY (
  echo Need either .NET Framework 3.5/4.x  or  Python 2.7.18 / 3.8+
  pause
  exit /b 1
)
set "PYTHONPATH=%CD%;%PYTHONPATH%"
%PY% "%~dp0grovekit\app.py"
if errorlevel 1 (
  %PY% -m grovekit.cli --browse
  pause
)
endlocal
