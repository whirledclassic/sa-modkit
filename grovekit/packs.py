# -*- coding: utf-8 -*-
from __future__ import print_function
import os
from grovekit.detect import file_size, join, kit_root

def _first_existing(candidates):
    for path in candidates:
        if os.path.isdir(path):
            return path
    return ""

def _resolve_ini_root(kit, local, sibling):
    if local:
        path = join(kit, local.replace("/", os.sep))
        if os.path.isdir(path):
            return path
    if sibling:
        parent = join(kit, os.pardir)
        for path in (join(parent, sibling), join(kit, "vendor", sibling), join(kit, "packs", sibling)):
            if os.path.isdir(path):
                return path
    return ""

def catalog_from_ini():
    kit = kit_root()
    path = join(kit, "packs.ini")
    if not os.path.isfile(path):
        return []
    packs, cur = [], None
    fh = open(path, "r")
    try:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith(";") or line.startswith("#"):
                continue
            if line.startswith("[") and line.endswith("]"):
                if cur:
                    packs.append(cur)
                cur = {"id": line[1:-1], "name": line[1:-1], "blurb": "", "keys": "", "repo": "", "root": "", "files": [], "compile": [], "_local": "", "_sib": ""}
                continue
            if cur is None or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip()
            if key == "name": cur["name"] = val
            elif key == "blurb": cur["blurb"] = val
            elif key == "keys": cur["keys"] = val
            elif key == "root_local": cur["_local"] = val
            elif key == "root_sibling": cur["_sib"] = val
            elif key == "min_source_bytes":
                try: cur["min_source_bytes"] = int(val)
                except ValueError: pass
            elif key == "file":
                parts = val.split("|")
                if len(parts) >= 2:
                    cur["files"].append((parts[0], parts[1], len(parts) > 2 and parts[2].strip() == "1"))
            elif key == "compile":
                parts = val.split("|")
                if len(parts) >= 2:
                    cur["compile"].append((parts[0], parts[1]))
        if cur:
            packs.append(cur)
    finally:
        fh.close()
    for pack in packs:
        pack["root"] = _resolve_ini_root(kit, pack.get("_local"), pack.get("_sib"))
        pack.pop("_local", None)
        pack.pop("_sib", None)
    return packs

def discover_pack_roots():
    root = kit_root()
    parent = join(root, os.pardir)
    return {
        "grovelink": _first_existing([join(parent, "gta-sa-win7-mods"), join(root, "vendor", "gta-sa-win7-mods"), join(root, "packs", "gta-sa-win7-mods")]),
        "awfps": _first_existing([join(parent, "sa-aw-fps"), join(root, "vendor", "sa-aw-fps"), join(root, "packs", "sa-aw-fps")]),
        "grovecast": _first_existing([join(root, "packs", "grovecast"), join(parent, "grovecast")]),
    }

def catalog():
    ini = catalog_from_ini()
    if ini:
        return ini
    roots = discover_pack_roots()
    return [{"id": "grovecast", "name": "GroveCast OBS slate", "blurb": "F3 live lower-third.", "root": roots.get("grovecast") or "", "repo": "https://github.com/whirledclassic/sa-modkit", "keys": "F3 slate", "files": [("obs/index.html", "CLEO/GroveLink/obs/index.html", False)], "compile": [("cleo/GroveCast.txt", "CLEO/GroveCast.cs")]}]

def pack_ready(pack):
    if not pack.get("root"):
        return False, "clone missing — %s" % pack.get("repo", "")
    for src, _dest in pack.get("compile", []):
        path = join(pack["root"], src.replace("/", os.sep))
        if not os.path.isfile(path):
            return False, "missing " + src
        need = pack.get("min_source_bytes") or 0
        if need and file_size(path) < need:
            return False, "stub source (%s bytes) — skip" % file_size(path)
    for src, _dest, _keep in pack.get("files", []):
        path = join(pack["root"], src.replace("/", os.sep))
        if not os.path.isfile(path):
            return False, "missing " + src
    return True, "ready"
