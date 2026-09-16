@echo off
setlocal EnableExtensions
title Build SA-Modkit.exe
cd /d "%~dp0"
set "CSC="
for %%P in (
  "%WINDIR%\Microsoft.NET\Framework\v4.0.30319\csc.exe"
  "%WINDIR%\Microsoft.NET\Framework\v3.5\csc.exe"
  "%WINDIR%\Microsoft.NET\Framework\v2.0.50727\csc.exe"
  "%WINDIR%\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
) do if exist %%~P if not defined CSC set "CSC=%%~P"
if not defined CSC (
  echo No csc.exe found.
  exit /b 1
)
echo Compiler: %CSC%
"%CSC%" /nologo /target:winexe /platform:x86 /out:"%~dp0SA-Modkit.exe" /r:System.dll /r:System.Windows.Forms.dll /r:System.Drawing.dll "%~dp0native\SAModkit.cs"
if errorlevel 1 (
  echo x86 flag not accepted, retrying without /platform...
  "%CSC%" /nologo /target:winexe /out:"%~dp0SA-Modkit.exe" /r:System.dll /r:System.Windows.Forms.dll /r:System.Drawing.dll "%~dp0native\SAModkit.cs"
)
if errorlevel 1 exit /b 1
echo OK  %~dp0SA-Modkit.exe
endlocal
