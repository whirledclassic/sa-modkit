# SA-Modkit.exe

The installer is a Win32 EXE. People do not need Python to install packs.

START.bat: launch existing EXE, else compile native\\SAModkit.cs with csc.exe (.NET 2/3.5/4 on Win7 through 11), else Python.

BUILD_EXE.bat only compiles. Output is 32-bit so one file covers 32-bit Windows 7 and 64-bit Windows 10/11.

Both clients read packs.ini.
