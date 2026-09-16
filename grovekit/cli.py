# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import os
import sys

_HERE = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from grovekit.choice import confirm_install, prompt_packs, ready_ids, save_choice
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
        description="SA Modkit %s — pick packs, then install (Win7+)." % KIT_VERSION
    )
    parser.add_argument("--gta", help="Folder that contains gta_sa.exe")
    parser.add_argument("--browse", action="store_true")
    parser.add_argument("--pack", action="append", dest="packs")
    parser.add_argument("--all", action="store_true", help="Every READY pack (still asks OK?)")
    parser.add_argument("--yes", action="store_true", help="Skip the OK? prompt")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)

    if args.list:
        for pack in catalog():
            ready, reason = pack_ready(pack)
            flag = "READY" if ready else "MISS "
            print("%s  %-16s  %s" % (flag, pack["id"], reason if not ready else pack["name"]))
        print("")
        print("Install only what you want:")
        print("  python -m grovekit.cli --browse --pack grovelink")
        print("  python -m grovekit.cli --browse --pack aw-fps")
        print("  python -m grovekit.cli --browse")
        print("Last form asks which packs. It does not install everything.")
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
        ids = ready_ids()
    elif args.packs:
        known = set(p["id"] for p in catalog())
        ids = []
        for pack_id in args.packs:
            if pack_id not in known:
                sys.stderr.write("unknown pack: %s\n" % pack_id)
                return 2
            ok, reason = pack_ready([p for p in catalog() if p["id"] == pack_id][0])
            if not ok:
                sys.stderr.write("skip %s -- %s\n" % (pack_id, reason))
            else:
                ids.append(pack_id)
    else:
        ids = prompt_packs()
        if ids is None:
            print("Cancelled.")
            return 0

    if not ids:
        print("Nothing selected. No files copied.")
        return 0

    info = inspect_game(gta)
    if not info["exe"]:
        sys.stderr.write("gta_sa.exe not in %s\n" % gta)
        return 2

    if not args.yes and not confirm_install(ids):
        print("Cancelled.")
        return 0

    save_choice(ids)
    ok = install_selected(gta, ids, log=Log())
    verify(gta, log=Log())
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
