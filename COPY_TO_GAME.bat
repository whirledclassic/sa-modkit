@echo off
setlocal EnableExtensions
title SA Modkit - copy to game
color 0A
cd /d "%~dp0"
echo.
echo   COPY TO GAME
echo   No Sanny. No Python. No compiler.
echo   Puts ready files into your GTA folder.
echo.
set "GTA="
if exist "%~dp0GTA_DIR.txt" set /p GTA=<"%~dp0GTA_DIR.txt"
if defined GTA if exist "%GTA%\gta_sa.exe" goto have_gta
echo Pick the folder that contains gta_sa.exe.
for /f "usebackq delims=" %%I in (`powershell -NoProfile -Command "Add-Type -AssemblyName System.Windows.Forms; $d = New-Object System.Windows.Forms.FolderBrowserDialog; $d.Description = 'Folder that contains gta_sa.exe'; if ($d.ShowDialog() -eq 'OK') { $d.SelectedPath }"`) do set "GTA=%%I"
if not defined GTA (
  echo Cancelled.
  pause
  exit /b 1
)
:have_gta
if not exist "%GTA%\gta_sa.exe" (
  echo No gta_sa.exe in:
  echo   %GTA%
  pause
  exit /b 1
)
echo Game: %GTA%
echo %GTA%>"%~dp0GTA_DIR.txt"
if not exist "%GTA%\CLEO.asi" (
  echo.
  echo CLEO.asi is missing. Download CLEO 4.4 from https://cleo.li
  echo Put CLEO.asi next to gta_sa.exe, then run this again.
  pause
  exit /b 1
)
mkdir "%GTA%\CLEO" 2>nul
mkdir "%GTA%\CLEO\GroveLink" 2>nul
mkdir "%GTA%\CLEO\GroveLink\obs" 2>nul
set COPIED=0
set MISSING=0
call :copy_if "%~dp0packs\grovecast\prebuilt\GroveCast.cs" "%GTA%\CLEO\GroveCast.cs"
call :copy_if "%~dp0packs\grovecast\obs\index.html" "%GTA%\CLEO\GroveLink\obs\index.html"
call :copy_if "%~dp0packs\grovecast\obs\serve.py" "%GTA%\CLEO\GroveLink\obs\serve.py"
call :copy_if "%~dp0packs\grovecast\obs\RUN_OBS.bat" "%GTA%\CLEO\GroveLink\obs\RUN_OBS.bat"
call :copy_if "%~dp0..\gta-sa-win7-mods\prebuilt\GroveLinkPhone.cs" "%GTA%\CLEO\GroveLinkPhone.cs"
call :copy_if "%~dp0..\gta-sa-win7-mods\prebuilt\MissionSwitcher.cs" "%GTA%\CLEO\MissionSwitcher.cs"
call :copy_if "%~dp0..\gta-sa-win7-mods\grovelink\GroveLink.fxt" "%GTA%\CLEO\GroveLink.fxt"
call :copy_if "%~dp0..\sa-aw-fps\prebuilt\AW_FPS_Core.cs" "%GTA%\CLEO\AW_FPS_Core.cs"
call :copy_if "%~dp0..\sa-aw-fps\prebuilt\AW_FPS_Combat.cs" "%GTA%\CLEO\AW_FPS_Combat.cs"
call :copy_if "%~dp0..\sa-aw-fps\prebuilt\AW_FPS_HUD.cs" "%GTA%\CLEO\AW_FPS_HUD.cs"
call :copy_if "%~dp0..\sa-aw-fps\prebuilt\AW_FPS_Loadout.cs" "%GTA%\CLEO\AW_FPS_Loadout.cs"
call :copy_if "%~dp0..\sa-aw-fps\config\aw_fps.ini" "%GTA%\modloader\SA_AW_FPS\config\aw_fps.ini"
echo.
echo Copied: %COPIED%
if %MISSING% GTR 0 (
  echo Some scripts are not in a prebuilt folder yet.
  echo Once those .cs files are dropped in prebuilt\, this copies them too.
)
echo Done. Launch gta_sa.exe.
pause
exit /b 0
:copy_if
if exist "%~1" (
  mkdir "%~dp2" 2>nul
  copy /Y "%~1" "%~2" >nul
  echo   ok    %~nx2
  set /a COPIED+=1
) else (
  set /a MISSING+=1
)
exit /b 0
