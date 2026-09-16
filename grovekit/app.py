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
    KIT_VERSION, catalog, guess_gta, inspect_game, install_selected,
    pack_ready, pick_folder, save_gta, verify, Log,
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

GREEN = "#c6ff7a"
BG = "#0c100c"
PANEL = "#151c15"
PANEL2 = "#1c251c"
FG = "#e4f5e4"
MUTED = "#7d9a7d"
ACCENT = "#3a7a32"
WARN = "#e0b44a"
BAD = "#e07070"

class App(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SA Modkit  " + KIT_VERSION)
        self.root.configure(bg=BG)
        self.root.minsize(820, 600)
        self.root.geometry("920x640")
        self.gta_var = tk.StringVar(value=guess_gta())
        self.status_var = tk.StringVar(value="")
        self.count_var = tk.StringVar(value="0 selected")
        self.pack_vars = {}
        self.pack_ready = {}
        self._busy = False
        self._build()
        self.refresh_detect()
        self._update_count()

    def _btn(self, parent, text, cmd, bg):
        return tk.Button(parent, text=text, command=cmd, bg=bg, fg=GREEN,
            activebackground=GREEN, activeforeground=BG, relief="flat", padx=12, pady=4)

    def _build(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=16, pady=(12, 4))
        left = tk.Frame(header, bg=BG)
        left.pack(side="left")
        tk.Label(left, text="SA MODKIT", fg=GREEN, bg=BG, font=("Segoe UI", 20, "bold")).pack(anchor="w")
        tk.Label(left, text="Windows 7 - 11   |   tick packs   |   nothing else is copied", fg=MUTED, bg=BG).pack(anchor="w")
        tk.Label(header, text="v" + KIT_VERSION, fg=MUTED, bg=BG, font=("Segoe UI", 10)).pack(side="right", pady=8)

        dest = tk.Frame(self.root, bg=PANEL)
        dest.pack(fill="x", padx=16, pady=8)
        tk.Label(dest, text="GAME FOLDER", fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", padx=12, pady=(8, 0))
        row = tk.Frame(dest, bg=PANEL)
        row.pack(fill="x", padx=12, pady=6)
        tk.Entry(row, textvariable=self.gta_var, bg="#0a0e0a", fg=FG, insertbackground=FG, relief="flat").pack(side="left", fill="x", expand=True, ipady=5)
        self._btn(row, "Browse...", self.browse, ACCENT).pack(side="left", padx=(8, 0))
        self.status_lbl = tk.Label(dest, textvariable=self.status_var, fg=GREEN, bg=PANEL, justify="left")
        self.status_lbl.pack(anchor="w", padx=12, pady=(0, 10))

        mid = tk.Frame(self.root, bg=BG)
        mid.pack(fill="both", expand=True, padx=16)
        leftp = tk.Frame(mid, bg=PANEL)
        leftp.pack(side="left", fill="both", expand=True, padx=(0, 8))
        head = tk.Frame(leftp, bg=PANEL)
        head.pack(fill="x", padx=8, pady=8)
        tk.Label(head, text="PACKS", fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(side="left")
        self._btn(head, "None", self.select_none, "#222").pack(side="right")
        self._btn(head, "Ready", self.select_ready, "#222").pack(side="right", padx=4)

        wrap = tk.Frame(leftp, bg=PANEL)
        wrap.pack(fill="both", expand=True)
        canvas = tk.Canvas(wrap, bg=PANEL, highlightthickness=0, bd=0)
        scroll = tk.Scrollbar(wrap, command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=PANEL)
        win = canvas.create_window((0, 0), window=inner, anchor="nw")
        def _stretch(event):
            canvas.itemconfigure(win, width=event.width)
        def _region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.bind("<Configure>", _stretch)
        inner.bind("<Configure>", _region)

        remembered = set(load_choice())
        for pack in catalog():
            ready, reason = pack_ready(pack)
            self.pack_ready[pack["id"]] = ready
            on = 1 if (ready and pack["id"] in remembered) else 0
            var = tk.IntVar(value=on)
            self.pack_vars[pack["id"]] = var
            card = tk.Frame(inner, bg=PANEL2)
            card.pack(fill="x", padx=8, pady=4)
            tk.Frame(card, bg=(GREEN if ready else BAD), width=4).pack(side="left", fill="y")
            body = tk.Frame(card, bg=PANEL2)
            body.pack(side="left", fill="x", expand=True, padx=8, pady=6)
            label = pack["name"] if ready else pack["name"] + "  --  " + reason
            chk = tk.Checkbutton(body, text=label, variable=var,
                fg=FG if ready else MUTED, bg=PANEL2, selectcolor="#0a0e0a",
                activebackground=PANEL2, activeforeground=GREEN,
                anchor="w", justify="left", highlightthickness=0,
                command=lambda pid=pack["id"]: self._on_toggle(pid))
            if not ready:
                chk.config(state="disabled")
            chk.pack(fill="x")
            keys = pack.get("keys") or ""
            extra = (pack.get("blurb") or "") + (("   |   " + keys) if keys else "")
            tk.Label(body, text=extra, fg=MUTED, bg=PANEL2, anchor="w", wraplength=400).pack(fill="x")
            var.trace("w", lambda *a: self._update_count())

        right = tk.Frame(mid, bg=PANEL)
        right.pack(side="left", fill="both", expand=True)
        tk.Label(right, text="LOG", fg=MUTED, bg=PANEL, font=("Segoe UI", 8)).pack(anchor="w", padx=10, pady=8)
        self.log_box = tk.Text(right, bg="#0a0e0a", fg=FG, height=14, wrap="word", relief="flat", insertbackground=FG)
        self.log_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=16, pady=12)
        self.install_btn = self._btn(bar, "Install selected", self.do_install, ACCENT)
        self.install_btn.pack(side="left")
        self._btn(bar, "Verify", self.do_verify, "#222").pack(side="left", padx=6)
        self._btn(bar, "Refresh", self.refresh_detect, "#222").pack(side="left")
        tk.Label(bar, textvariable=self.count_var, fg=MUTED, bg=BG).pack(side="right")

    def _update_count(self):
        self.count_var.set("%d selected" % len(self._selected_ids()))

    def _on_toggle(self, pack_id):
        if pack_id == "switcher-full" and self.pack_vars.get("switcher-full") and self.pack_vars["switcher-full"].get():
            if "switcher-skin" in self.pack_vars:
                self.pack_vars["switcher-skin"].set(0)
        if pack_id == "switcher-skin" and self.pack_vars.get("switcher-skin") and self.pack_vars["switcher-skin"].get():
            if "switcher-full" in self.pack_vars:
                self.pack_vars["switcher-full"].set(0)
        self._update_count()

    def select_none(self):
        for var in self.pack_vars.values():
            var.set(0)
        self._update_count()

    def select_ready(self):
        for pack_id, var in self.pack_vars.items():
            var.set(1 if self.pack_ready.get(pack_id) else 0)
        if self.pack_ready.get("switcher-full") and "switcher-skin" in self.pack_vars:
            self.pack_vars["switcher-skin"].set(0)
        self._update_count()

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
            bits = [info["kind"], "CLEO " + ("yes" if info["cleo"] else "NO"),
                    "SilentPatch " + ("yes" if info["silentpatch"] else "no"),
                    "Sanny " + ("yes" if info["sanny"] else "NO")]
            self.status_var.set("   |   ".join(bits))
            kind = info["kind"] or ""
            if (not info["cleo"]) or ("Steam" in kind) or ("3.0" in kind):
                self.status_lbl.configure(fg=WARN)
            else:
                self.status_lbl.configure(fg=GREEN)
        else:
            self.status_var.set("No gta_sa.exe in that folder")
            self.status_lbl.configure(fg=BAD)

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
        self.install_btn.config(state="disabled", text="Installing...")
        self.log("install  " + ", ".join(ids))
        def work():
            try:
                install_selected(gta, ids, log=Log(self.log))
            except Exception as err:
                self.log("FAIL  " + str(err))
            finally:
                self._busy = False
                def _done():
                    self.install_btn.config(state="normal", text="Install selected")
                    self.refresh_detect()
                self.root.after(0, _done)
        threading.Thread(target=work).start()

    def do_verify(self):
        verify(self.gta_var.get().strip(), log=Log(self.log))

    def run(self):
        self.root.mainloop()

def main():
    App().run()

if __name__ == "__main__":
    main()
