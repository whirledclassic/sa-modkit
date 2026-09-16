# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import subprocess
import sys

PY2 = sys.version_info[0] == 2


def kit_root():
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.abspath(os.path.join(here, os.pardir))


def _norm(path):
    return os.path.normpath(path)


def join(*parts):
    return _norm(os.path.join(*parts))


def file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def read_text(path):
    try:
        fh = open(path, "r")
        try:
            return fh.read().strip()
        finally:
            fh.close()
    except (IOError, OSError):
        return ""


def write_text(path, text):
    fh = open(path, "w")
    try:
        fh.write(text)
        if not text.endswith("\n"):
            fh.write("\n")
    finally:
        fh.close()


def pick_folder(title="Select the folder that contains gta_sa.exe"):
    try:
        if PY2:
            import Tkinter as tk
            import tkFileDialog as fd
        else:
            import tkinter as tk
            from tkinter import filedialog as fd
        root = tk.Tk()
        root.withdraw()
        try:
            root.wm_attributes("-topmost", 1)
        except Exception:
            pass
        path = fd.askdirectory(title=title, mustexist=True)
        root.destroy()
        if path:
            return _norm(path)
    except Exception:
        pass
    if os.name == "nt":
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$d = New-Object System.Windows.Forms.FolderBrowserDialog; "
            "$d.Description = '%s'; "
            "$d.ShowNewFolderButton = $false; "
            "if ($d.ShowDialog() -eq 'OK') { $d.SelectedPath }"
        ) % title.replace("'", "''")
        try:
            out = subprocess.check_output(
                ["powershell", "-NoProfile", "-Command", ps],
                stderr=subprocess.STDOUT,
                universal_newlines=True,
            )
            path = out.strip().strip('"')
            if path and os.path.isdir(path):
                return _norm(path)
        except Exception:
            pass
    return ""


COMMON_GTA = [
    r"C:\Program Files (x86)\Rockstar Games\GTA San Andreas",
    r"C:\Program Files\Rockstar Games\GTA San Andreas",
    r"C:\Program Files\Rockstar Games\Grand Theft Auto San Andreas",
    r"C:\GTA San Andreas",
    r"D:\GTA San Andreas",
    r"E:\GTA San Andreas",
    r"C:\Games\GTA San Andreas",
    r"D:\Games\GTA San Andreas",
    r"E:\Games\GTA San Andreas",
    r"C:\Program Files (x86)\Steam\steamapps\common\Grand Theft Auto San Andreas",
    r"C:\Program Files\Steam\steamapps\common\Grand Theft Auto San Andreas",
    r"D:\SteamLibrary\steamapps\common\Grand Theft Auto San Andreas",
    r"E:\SteamLibrary\steamapps\common\Grand Theft Auto San Andreas",
    r"C:\Steam\steamapps\common\Grand Theft Auto San Andreas",
    r"D:\Steam\steamapps\common\Grand Theft Auto San Andreas",
]

COMMON_SANNY = [
    r"C:\Program Files\Sanny Builder 4\sanny.exe",
    r"C:\Program Files\Sanny Builder 3\sanny.exe",
    r"C:\Program Files (x86)\Sanny Builder 4\sanny.exe",
    r"C:\Program Files (x86)\Sanny Builder 3\sanny.exe",
    r"C:\Sanny Builder 4\sanny.exe",
    r"C:\Sanny Builder 3\sanny.exe",
    r"D:\Sanny Builder 4\sanny.exe",
    r"D:\Sanny Builder 3\sanny.exe",
]


def remember_path():
    return join(kit_root(), "GTA_DIR.txt")


def load_saved_gta():
    path = read_text(remember_path())
    if path and os.path.isfile(join(path, "gta_sa.exe")):
        return _norm(path)
    return ""


def save_gta(path):
    write_text(remember_path(), _norm(path))


def guess_gta():
    saved = load_saved_gta()
    if saved:
        return saved
    for folder in COMMON_GTA:
        if os.path.isfile(join(folder, "gta_sa.exe")):
            return _norm(folder)
    return ""


def _which(name):
    paths = os.environ.get("PATH", "").split(os.pathsep)
    exts = [""]
    if os.name == "nt":
        exts = os.environ.get("PATHEXT", ".EXE;.BAT;.CMD").split(";")
    for directory in paths:
        for ext in exts:
            candidate = join(directory, name + ext)
            if os.path.isfile(candidate):
                return candidate
    return ""


def find_sanny():
    for folder in COMMON_SANNY:
        if os.path.isfile(folder):
            return _norm(folder)
    home = os.path.expanduser("~")
    for folder in (
        join(home, "Desktop", "Sanny Builder 4", "sanny.exe"),
        join(home, "Desktop", "Sanny Builder 3", "sanny.exe"),
        join(home, "Documents", "Sanny Builder 4", "sanny.exe"),
        join(home, "Documents", "Sanny Builder 3", "sanny.exe"),
    ):
        if os.path.isfile(folder):
            return _norm(folder)
    return _which("sanny.exe") or _which("sanny") or ""


def _exe_kind(gta_dir):
    size = file_size(join(gta_dir, "gta_sa.exe"))
    if size < 0:
        return "missing"
    if 13000000 <= size <= 16000000:
        return "likely 1.0 (~14 MB) — CLEO packs target this"
    if size > 20000000:
        return "likely Steam/re-release — downgrade to 1.0 before CLEO"
    return "unknown build (%s bytes)" % size


def inspect_game(gta_dir):
    info = {
        "ok": False,
        "gta": gta_dir or "",
        "exe": False,
        "kind": "missing",
        "cleo": False,
        "inifiles": False,
        "asi_loader": False,
        "silentpatch": False,
        "modloader": False,
        "writable": False,
        "warnings": [],
        "sanny": find_sanny(),
    }
    if not gta_dir or not os.path.isdir(gta_dir):
        info["warnings"].append("Pick the folder that contains gta_sa.exe.")
        return info
    info["exe"] = os.path.isfile(join(gta_dir, "gta_sa.exe"))
    if not info["exe"]:
        info["warnings"].append("gta_sa.exe not in that folder.")
        return info
    info["kind"] = _exe_kind(gta_dir)
    info["cleo"] = os.path.isfile(join(gta_dir, "CLEO.asi"))
    info["inifiles"] = os.path.isfile(join(gta_dir, "CLEO", "IniFiles.cleo"))
    info["asi_loader"] = (
        os.path.isfile(join(gta_dir, "dinput8.dll"))
        or os.path.isfile(join(gta_dir, "vorbisHooked.dll"))
        or info["cleo"]
    )
    info["silentpatch"] = os.path.isfile(join(gta_dir, "SilentPatchSA.asi"))
    info["modloader"] = os.path.isfile(join(gta_dir, "modloader.asi")) or os.path.isdir(
        join(gta_dir, "modloader")
    )
    info["writable"] = os.access(gta_dir, os.W_OK)
    if not info["cleo"]:
        info["warnings"].append("CLEO.asi missing. Install CLEO 4.4 from https://cleo.li")
    if not info["silentpatch"]:
        info["warnings"].append(
            "SilentPatchSA.asi missing. https://cookieplmonster.github.io/mods/gta-sa/"
        )
    if "Steam/re-release" in info["kind"]:
        info["warnings"].append("Downgrade to 1.0 Hoodlum or most CLEO/ASI packs will not load.")
    if not info["writable"]:
        info["warnings"].append("Folder is not writable. Run START.bat as administrator.")
    info["ok"] = True
    return info
