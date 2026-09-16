# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import shutil
import subprocess

from grovekit.detect import (
    PY2,
    ensure_dir,
    file_size,
    guess_gta,
    inspect_game,
    join,
    pick_folder,
    save_gta,
    write_text,
)
from grovekit.packs import catalog, pack_ready

KIT_VERSION = "0.1.0"


class Log(object):
    def __init__(self, callback=None):
        self.callback = callback
        self.lines = []

    def __call__(self, msg):
        self.lines.append(msg)
        if self.callback:
            self.callback(msg)
        else:
            print(msg)


def _copy_file(src, dest, keep_existing, log):
    ensure_dir(os.path.dirname(dest))
    if keep_existing and os.path.isfile(dest):
        log("keep    " + dest)
        return True
    shutil.copy2(src, dest)
    log("copy    " + dest)
    return True


def _compile_sanny(sanny, src, dest, log):
    ensure_dir(os.path.dirname(dest))
    log("sanny   " + os.path.basename(src))
    try:
        proc = subprocess.Popen(
            [sanny, "--compile", src, dest],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        out, _unused = proc.communicate()
        if proc.returncode not in (0, None) and not os.path.isfile(dest):
            log("FAIL    sanny exit %s" % proc.returncode)
            if out:
                text = out if PY2 else out.decode("mbcs", "replace")
                log(text[:400])
            return False
    except OSError as err:
        log("FAIL    sanny: %s" % err)
        return False
    if os.path.isfile(dest) and file_size(dest) >= 32:
        log("ok      %s (%s bytes)" % (dest, file_size(dest)))
        return True
    log("FAIL    no output " + dest)
    return False


def install_pack(pack, gta_dir, sanny, log):
    ok, reason = pack_ready(pack)
    if not ok:
        log("skip    %s — %s" % (pack["id"], reason))
        return False
    log("----    " + pack["name"])
    root = pack["root"]
    failed = 0
    for src_rel, dest_rel, keep in pack.get("files", []):
        src = join(root, src_rel.replace("/", os.sep))
        dest = join(gta_dir, dest_rel.replace("/", os.sep))
        try:
            _copy_file(src, dest, keep, log)
        except (IOError, OSError) as err:
            log("FAIL    copy %s: %s" % (src_rel, err))
            failed += 1
    for src_rel, dest_rel in pack.get("compile", []):
        src = join(root, src_rel.replace("/", os.sep))
        dest = join(gta_dir, dest_rel.replace("/", os.sep))
        need = pack.get("min_source_bytes") or 0
        if need and file_size(src) < need:
            log("skip    stub " + src_rel)
            continue
        if not sanny:
            log("WARN    no Sanny — copy source next to dest for manual F7")
            try:
                _copy_file(src, dest + ".txt", False, log)
            except (IOError, OSError) as err:
                log("FAIL    %s" % err)
                failed += 1
            continue
        if not _compile_sanny(sanny, src, dest, log):
            failed += 1
    return failed == 0


def install_selected(gta_dir, pack_ids, log=None):
    log = log or Log()
    info = inspect_game(gta_dir)
    if not info["exe"]:
        log("No gta_sa.exe in " + (gta_dir or "(empty)"))
        return False
    save_gta(gta_dir)
    ensure_dir(join(gta_dir, "CLEO"))
    ensure_dir(join(gta_dir, "CLEO", "GroveLink"))
    sanny = info["sanny"]
    log("Sanny   " + (sanny or "not found — scripts copied as .txt"))
    packs = [p for p in catalog() if p["id"] in set(pack_ids)]
    if not packs:
        log("Nothing selected.")
        return False
    full = [p for p in packs if p["id"] == "switcher-full"]
    if full and pack_ready(full[0])[0]:
        packs = [p for p in packs if p["id"] != "switcher-skin"]
        log("using   full companion switcher")
    ok_all = True
    for pack in packs:
        if not install_pack(pack, gta_dir, sanny, log):
            ok_all = False
    write_text(
        join(gta_dir, "CLEO", "GroveLink", "modkit.txt"),
        "sa-modkit %s\npacks=%s\n" % (KIT_VERSION, ",".join(pack_ids)),
    )
    log("done    sa-modkit " + KIT_VERSION)
    return ok_all


def verify(gta_dir, log=None):
    log = log or Log()
    info = inspect_game(gta_dir)
    log("game    " + (gta_dir or "?"))
    log("exe     " + info["kind"])
    log("CLEO    " + ("yes" if info["cleo"] else "NO"))
    log("IniFiles " + ("yes" if info["inifiles"] else "no"))
    log("SilentPatch " + ("yes" if info["silentpatch"] else "no"))
    log("ModLoader " + ("yes" if info["modloader"] else "no"))
    log("Sanny   " + (info["sanny"] or "NO"))
    for rel, minimum in (
        ("CLEO/GroveLinkPhone.cs", 200),
        ("CLEO/GroveLink.fxt", 100),
        ("CLEO/MissionSwitcher.cs", 200),
        ("CLEO/AW_FPS_Core.cs", 200),
        ("CLEO/AW_FPS_Combat.cs", 200),
        ("CLEO/AW_FPS_HUD.cs", 200),
        ("CLEO/AW_FPS_Loadout.cs", 200),
    ):
        path = join(gta_dir, rel.replace("/", os.sep))
        size = file_size(path)
        if size >= minimum:
            log("ok      %s (%s)" % (rel, size))
        elif size >= 0:
            log("tiny    %s (%s) — stub?" % (rel, size))
        else:
            log("miss    " + rel)
    for warning in info["warnings"]:
        log("warn    " + warning)
    return info
