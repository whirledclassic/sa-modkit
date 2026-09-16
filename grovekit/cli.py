# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import sys

_HERE = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from grovekit.engine import (
    KIT_VERSION,
    catalog,
    guess_gta,
    inspect_game,
    install_selected,
    pack_ready,
    pick_folder,
    verify,
    Log,
)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="SA Modkit %s — install whirledclassic GTA SA packs (Win7+)."
        % KIT_VERSION
    )
    parser.add_argument("--gta", help="Folder that contains gta_sa.exe")
    parser.add_argument("--browse", action="store_true", help="Open a folder dialog first")
    parser.add_argument("--pack", action="append", dest="packs", help="Pack id (repeatable)")
    parser.add_argument("--all", action="store_true", help="Every pack whose source is ready")
    parser.add_argument("--list", action="store_true", help="Show packs and exit")
    parser.add_argument("--verify", action="store_true", help="Only verify, do not copy")
    args = parser.parse_args(argv)

    if args.list:
        for pack in catalog():
            ready, reason = pack_ready(pack)
            flag = "READY" if ready else "MISS "
            print("%s  %-16s  %s" % (flag, pack["id"], reason if not ready else pack["name"]))
        return 0

    gta = args.gta or guess_gta()
    if args.browse or not gta:
        picked = pick_folder()
        if picked:
            gta = picked
    if not gta:
        sys.stderr.write("Pass --gta path or use --browse\n")
        return 2

    if args.verify:
        verify(gta, log=Log())
        return 0

    if args.all:
        ids = [p["id"] for p in catalog() if pack_ready(p)[0]]
    elif args.packs:
        ids = args.packs
    else:
        ids = [p["id"] for p in catalog() if pack_ready(p)[0] and p["id"] != "switcher-full"]

    info = inspect_game(gta)
    if not info["exe"]:
        sys.stderr.write("gta_sa.exe not in %s\n" % gta)
        return 2
    ok = install_selected(gta, ids, log=Log())
    verify(gta, log=Log())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
