# SA Modkit

Win7-and-newer **mod client** for the whirledclassic GTA San Andreas packs.

You pick the game folder. You tick packs. It copies files and compiles CLEO.

**Repo:** https://github.com/whirledclassic/sa-modkit

Does **not** ship `gta_sa.exe`, `.img`, or anyone else’s closed assets.

## Why this exists

Each pack had its own INSTALL.bat / COMPILE.bat. Those still work. This kit is the shared front door:

- One destination picker (Browse dialog, works on Windows 7)
- One compatibility check (1.0 vs Steam 3.0, CLEO, SilentPatch, Sanny)
- One place to register a **new** pack when you write the next mod
- Same code path on Windows 7 SP1 and Windows 11

## Supported Windows

| OS | Python | Notes |
|---|---|---|
| Windows 7 SP1 | **2.7.18** or **3.8.10** | 3.9+ dropped Win7 |
| Windows 8.1 | 2.7 / 3.4–3.8 | |
| Windows 10 / 11 | 3.8–3.12 | Tick Add python.exe to PATH |

No .NET 6, no WinUI, no PowerShell 7. Folder dialog falls back to PowerShell 2 FolderBrowserDialog if tkinter is missing.

## Layout on disk

```
mods/
  sa-modkit/                 double-click START.bat here
  gta-sa-win7-mods/          GroveLink + switcher
  sa-aw-fps/                 exo FPS layer
```

The engine looks at `../gta-sa-win7-mods` and `../sa-aw-fps`. You can also drop copies under `sa-modkit/vendor/`.

## Run

```
START.bat
```

Or:

```
python -m grovekit
python -m grovekit.cli --browse --all
python -m grovekit.cli --gta "D:\GTA San Andreas" --pack grovelink --pack aw-fps
python -m grovekit.cli --list
python -m grovekit.cli --gta "D:\GTA San Andreas" --verify
```

## Packs it knows today

| id | In-game |
|---|---|
| `grovelink` | **K** green phone |
| `switcher-skin` | **H** look like the homie, **J** CJ |
| `switcher-full` | **H** become them — skipped if the source is still a stub |
| `aw-fps` | Exo dash/boost, **F4** toggle, **8/9/0** classes |

Key split: GroveLink **K**, switcher **H/F6**, AW pack **F4**.

## Add your next mod

1. Put the repo next to `sa-modkit` (or under `vendor/`).
2. Open `grovekit/engine.py` → `catalog()` and append a dict.
3. `python -m grovekit.cli --list` until it prints READY.

See [docs/PACK_FORMAT.md](docs/PACK_FORMAT.md).

## Related

- https://github.com/whirledclassic/gta-sa-win7-mods
- https://github.com/whirledclassic/sa-aw-fps

MIT for this kit’s original code.
