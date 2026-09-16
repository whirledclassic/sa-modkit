# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import threading

_HERE = os.path.abspath(os.path.dirname(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, os.pardir))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from grovekit.choice import load_choice, save_choice
from grovekit.engine import (
    KIT_VERSION,
    catalog,
    guess_gta,
    inspect_game,
    install_selected,
    pack_ready,
    pick_folder,
    save_gta,
    verify,
    Log,
)

try:
    if sys.version_info[0] == 2:
        import Tkinter as tk
        import tkMessageBox as messagebox
    else:
        import tkinter as tk
        from tkinter import messagebox
except ImportError:
    sys.stderr.write("tkinter missing. Use: python -m grovekit.cli --browse\n")
    sys.exit(2)

GREEN = "#b6ff6b"
BG = "#101410"
PANEL = "#1a221a"
FG = "#d8f5d8"
MUTED = "#7a9a7a"
ACCENT = "#2f5d2f"


class App(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SA Modkit  " + KIT_VERSION)
        self.root.configure(bg=BG)
        self.root.minsize(740, 560)
        self.gta_var = tk.StringVar(value=guess_gta())
        self.status_var = tk.StringVar(value="")
        self.pack_vars = {}
        self.pack_ready = {}
        self._busy = False
        self._build()
        self.refresh_detect()

    def _build(self):
        top = tk.Frame(self.root, bg=BG)
        top.pack(fill="x", padx=12, pady=8)
        tk.Label(top, text="SA MODKIT", fg=GREEN, bg=BG, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(top, text="Tick only the packs you want. Unticked packs are not copied.", fg=MUTED, bg=BG).pack(anchor="w")

        dest = tk.Frame(self.root, bg=PANEL)
        dest.pack(fill="x", padx=12, pady=6)
        tk.Label(dest, text="GTA San Andreas folder", fg=MUTED, bg=PANEL).pack(anchor="w", padx=8, pady=(8, 0))
        row = tk.Frame(dest, bg=PANEL)
        row.pack(fill="x", padx=8, pady=6)
        tk.Entry(row, textvariable=self.gta_var, bg="#0d120d", fg=FG, insertbackground=FG).pack(side="left", fill="x", expand=True, ipady=3)
        tk.Button(row, text="Browse...", command=self.browse, bg=ACCENT, fg=GREEN).pack(side="left", padx=6)
        tk.Label(dest, textvariable=self.status_var, fg=GREEN, bg=PANEL, justify="left").pack(anchor="w", padx=8, pady=(0, 8))

        mid = tk.Frame(self.root, bg=BG)
        mid.pack(fill="both", expand=True, padx=12)
        left = tk.Frame(mid, bg=PANEL)
        left.pack(side="left", fill="both", expand=True, padx=(0, 6))
        head = tk.Frame(left, bg=PANEL)
        head.pack(fill="x", padx=8, pady=6)
        tk.Label(head, text="Packs  (all off until you tick them)", fg=MUTED, bg=PANEL).pack(side="left")
        tk.Button(head, text="None", command=self.select_none, bg="#222", fg=GREEN).pack(side="right")
        tk.Button(head, text="Ready", command=self.select_ready, bg="#222", fg=GREEN).pack(side="right", padx=4)

        remembered = set(load_choice())
        for pack in catalog():
            ready, reason = pack_ready(pack)
            self.pack_ready[pack["id"]] = ready
            on = 1 if (ready and pack["id"] in remembered) else 0
            var = tk.IntVar(value=on)
            self.pack_vars[pack["id"]] = var
            label = pack["name"] if ready else pack["name"] + "  --  " + reason
            chk = tk.Checkbutton(
                left, text=label, variable=var,
                fg=FG if ready else MUTED, bg=PANEL, selectcolor="#0d120d",
                activebackground=PANEL, activeforeground=GREEN,
                anchor="w", justify="left",
                command=lambda pid=pack["id"]: self._on_toggle(pid),
            )
            if not ready:
                chk.config(state="disabled")
            chk.pack(fill="x", padx=8)
            tk.Label(left, text="    " + pack["blurb"] + "  [" + pack.get("keys", "") + "]", fg=MUTED, bg=PANEL, anchor="w", wraplength=380).pack(fill="x", padx=8, pady=(0, 6))

        right = tk.Frame(mid, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="Log", fg=MUTED, bg=PANEL).pack(anchor="w", padx=8, pady=6)
        self.log_box = tk.Text(right, bg="#0d120d", fg=FG, height=14, wrap="word")
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=12, pady=10)
        tk.Button(bar, text="Install selected", command=self.do_install, bg=ACCENT, fg=GREEN).pack(side="left")
        tk.Button(bar, text="Verify", command=self.do_verify, bg="#222", fg=GREEN).pack(side="left", padx=8)
        tk.Button(bar, text="Refresh", command=self.refresh_detect, bg="#222", fg=GREEN).pack(side="left")
        tk.Label(bar, text="Unticked = left alone", fg=MUTED, bg=BG).pack(side="right")

    def _on_toggle(self, pack_id):
        if pack_id == "switcher-full" and self.pack_vars.get("switcher-full") and self.pack_vars["switcher-full"].get():
            if "switcher-skin" in self.pack_vars:
                self.pack_vars["switcher-skin"].set(0)
        if pack_id == "switcher-skin" and self.pack_vars.get("switcher-skin") and self.pack_vars["switcher-skin"].get():
            if "switcher-full" in self.pack_vars:
                self.pack_vars["switcher-full"].set(0)

    def select_none(self):
        for var in self.pack_vars.values():
            var.set(0)

    def select_ready(self):
        for pack_id, var in self.pack_vars.items():
            var.set(1 if self.pack_ready.get(pack_id) else 0)
        if self.pack_ready.get("switcher-full") and "switcher-skin" in self.pack_vars:
            self.pack_vars["switcher-skin"].set(0)

    def _selected_ids(self):
        return [pid for pid, var in self.pack_vars.items() if var.get() and self.pack_ready.get(pid)]

    def log(self, msg):
        def _append():
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
        self.root.after(0, _append)

    def browse(self):
        path = pick_folder()
        if path:
            self.gta_var.set(path)
            save_gta(path)
            self.refresh_detect()

    def refresh_detect(self):
        info = inspect_game(self.gta_var.get().strip())
        if info["exe"]:
            self.status_var.set("  |  ".join([
                info["kind"],
                "CLEO " + ("yes" if info["cleo"] else "NO"),
                "SilentPatch " + ("yes" if info["silentpatch"] else "no"),
                "Sanny " + ("yes" if info["sanny"] else "NO"),
            ]))
        else:
            self.status_var.set("No game selected")

    def do_install(self):
        if self._busy:
            return
        gta = self.gta_var.get().strip()
        if not inspect_game(gta)["exe"]:
            messagebox.showerror("SA Modkit", "Pick the folder that contains gta_sa.exe.")
            return
        ids = self._selected_ids()
        if not ids:
            messagebox.showinfo("SA Modkit", "No packs ticked.\nTick one or more, or press Ready then untick what you do not want.")
            return
        if not messagebox.askyesno("SA Modkit", "Install only these?\n\n" + "\n".join(ids)):
            return
        save_choice(ids)
        self._busy = True
        self.log("install " + ", ".join(ids))

        def work():
            try:
                install_selected(gta, ids, log=Log(self.log))
            except Exception as err:
                self.log("FAIL  " + str(err))
            finally:
                self._busy = False
                self.root.after(0, self.refresh_detect)
        threading.Thread(target=work).start()

    def do_verify(self):
        verify(self.gta_var.get().strip(), log=Log(self.log))

    def run(self):
        self.root.mainloop()


def main():
    App().run()


if __name__ == "__main__":
    main()
