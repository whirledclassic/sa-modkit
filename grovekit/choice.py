# -*- coding: utf-8 -*-
from __future__ import print_function

from grovekit.detect import kit_root, read_text, write_text, join
from grovekit.packs import catalog, pack_ready

try:
    ask = raw_input
except NameError:
    ask = input


def choice_path():
    return join(kit_root(), "SELECTED.txt")


def load_choice():
    raw = read_text(choice_path())
    if not raw:
        return []
    parts = raw.replace(",", " ").replace(";", " ").split()
    known = set(p["id"] for p in catalog())
    return [p for p in parts if p in known]


def save_choice(ids):
    write_text(choice_path(), " ".join(ids))


def ready_ids():
    return [p["id"] for p in catalog() if pack_ready(p)[0]]


def prompt_packs():
    packs = catalog()
    print("")
    print("  #   id                status")
    print("  --  ----------------  ------")
    for i, pack in enumerate(packs, 1):
        ready, reason = pack_ready(pack)
        flag = "READY" if ready else "MISS "
        extra = "" if ready else "  (%s)" % reason
        print("  %-2s  %-16s  %s%s" % (i, pack["id"], flag, extra))
    print("")
    print("Type pack numbers or ids, separated by spaces.")
    print("Examples:  1 4     grovelink aw-fps     ready     none")
    print("Enter alone cancels. Nothing is installed until you confirm.")
    line = ask("> ").strip()
    if not line:
        return None
    if line.lower() in ("none", "n", "cancel", "q", "quit"):
        return []
    if line.lower() in ("ready", "r", "available", "all", "a"):
        return ready_ids()
    chosen = []
    known = {p["id"]: p for p in packs}
    for token in line.replace(",", " ").split():
        if token.isdigit():
            idx = int(token)
            if 1 <= idx <= len(packs):
                chosen.append(packs[idx - 1]["id"])
                continue
        if token in known:
            chosen.append(token)
            continue
        print("unknown pack: %s" % token)
    kept = []
    for pack_id in chosen:
        pack = known[pack_id]
        ok, reason = pack_ready(pack)
        if ok:
            kept.append(pack_id)
        else:
            print("skip %s -- %s" % (pack_id, reason))
    return kept


def confirm_install(ids):
    if not ids:
        print("No packs selected.")
        return False
    print("Will install: %s" % ", ".join(ids))
    ans = ask("OK? [y/N] ").strip().lower()
    return ans in ("y", "yes")
