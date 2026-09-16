# -*- coding: utf-8 -*-
"""Register new mods here. See docs/PACK_FORMAT.md."""
from __future__ import print_function

import os
from grovekit.detect import file_size, join, kit_root


def _first_existing(candidates):
    for path in candidates:
        if os.path.isdir(path):
            return path
    return ""


def discover_pack_roots():
    root = kit_root()
    parent = join(root, os.pardir)
    return {
        "grovelink": _first_existing(
            [
                join(parent, "gta-sa-win7-mods"),
                join(root, "vendor", "gta-sa-win7-mods"),
                join(root, "packs", "gta-sa-win7-mods"),
            ]
        ),
        "awfps": _first_existing(
            [
                join(parent, "sa-aw-fps"),
                join(root, "vendor", "sa-aw-fps"),
                join(root, "packs", "sa-aw-fps"),
            ]
        ),
    }


def catalog():
    roots = discover_pack_roots()
    gl = roots["grovelink"]
    aw = roots["awfps"]
    return [
        {
            "id": "grovelink",
            "name": "GroveLink Phone",
            "blurb": "K opens the green handset. Bridge on port 8088.",
            "root": gl,
            "repo": "https://github.com/whirledclassic/gta-sa-win7-mods",
            "keys": "K phone",
            "files": [
                ("grovelink/GroveLink.fxt", "CLEO/GroveLink.fxt", False),
                ("grovelink/GroveLink/link.ini", "CLEO/GroveLink/link.ini", True),
            ],
            "compile": [("grovelink/GroveLinkPhone.txt", "CLEO/GroveLinkPhone.cs")],
        },
        {
            "id": "switcher-skin",
            "name": "Companion skin switcher",
            "blurb": "H look like the nearest homie. J back to CJ. Safe default.",
            "root": gl,
            "repo": "https://github.com/whirledclassic/gta-sa-win7-mods",
            "keys": "H skin  J CJ",
            "files": [],
            "compile": [("switcher/MissionSwitcher_SkinOnly.txt", "CLEO/MissionSwitcher.cs")],
        },
        {
            "id": "switcher-full",
            "name": "Companion body switcher (full)",
            "blurb": "H become them, CJ stays. Skipped if the source is still a stub.",
            "root": gl,
            "repo": "https://github.com/whirledclassic/gta-sa-win7-mods",
            "keys": "H become  F6  G next  J CJ",
            "files": [],
            "compile": [("switcher/MissionSwitcher.txt", "CLEO/MissionSwitcher.cs")],
            "min_source_bytes": 2000,
        },
        {
            "id": "aw-fps",
            "name": "SA \u00b7 AW FPS",
            "blurb": "Exo dash/boost, hitmarkers, 8/9/0 classes. Toggle F4.",
            "root": aw,
            "repo": "https://github.com/whirledclassic/sa-aw-fps",
            "keys": "F4 toggle  8/9/0 classes  double-tap WASD dash",
            "files": [("config/aw_fps.ini", "modloader/SA_AW_FPS/config/aw_fps.ini", False)],
            "compile": [
                ("cleo/AW_FPS_Core.txt", "CLEO/AW_FPS_Core.cs"),
                ("cleo/AW_FPS_Combat.txt", "CLEO/AW_FPS_Combat.cs"),
                ("cleo/AW_FPS_HUD.txt", "CLEO/AW_FPS_HUD.cs"),
                ("cleo/AW_FPS_Loadout.txt", "CLEO/AW_FPS_Loadout.cs"),
            ],
        },
    ]


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
