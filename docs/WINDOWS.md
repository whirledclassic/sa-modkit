# Windows 7 through 11

Written against CPython 2.7 + 3.4–3.12 and the cmd.exe that shipped with Windows 7.

Refuses to depend on: PowerShell 5+ only cmdlets, Windows Terminal, .NET 6/8, WinGet, pathlib as a required import.

Folder picker: tkinter askdirectory, then PowerShell 2 FolderBrowserDialog, then `--gta`.

Game in Program Files: run START.bat as administrator or install GTA somewhere writable.

Windows 7 Python must be 2.7.18 or 3.8.10. Python 3.9 dropped Windows 7.
