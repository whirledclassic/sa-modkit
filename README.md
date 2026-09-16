# SA Modkit

Win7-and-newer **mod client** for the whirledclassic GTA San Andreas packs.

You pick the game folder. **You tick only the packs you want.** Unticked packs are not copied.

**Repo:** https://github.com/whirledclassic/sa-modkit

Does **not** ship `gta_sa.exe`, `.img`, or anyone else’s closed assets.

## Run

```
START.bat
```

Boxes start **unchecked**. Tick GroveLink, or AW FPS, or both — then Install selected. Confirm the list.

Shortcuts: **None** clears ticks. **Ready** ticks every pack whose source is on disk. Missing clones are greyed out.

CLI (same rule — no silent install-everything):

```
python -m grovekit.cli --list
python -m grovekit.cli --browse --pack grovelink
python -m grovekit.cli --browse --pack aw-fps
python -m grovekit.cli --browse
python -m grovekit.cli --gta "D:\GTA San Andreas" --pack grovelink --pack aw-fps --yes
```

`--browse` with no `--pack` prints a numbered list. Type `1 4` or `grovelink aw-fps`. Empty line cancels. `--all` still asks `OK?` unless you pass `--yes`.

## Layout on disk

```
mods/
  sa-modkit/
  gta-sa-win7-mods/
  sa-aw-fps/
```

## Packs

| id | In-game |
|---|---|
| `grovelink` | **K** green phone |
| `switcher-skin` | **H** look like the homie, **J** CJ |
| `switcher-full` | **H** become them — skipped if the source is still a stub |
| `aw-fps` | Exo dash/boost, **F4** toggle, **8/9/0** classes |

Skin and full switcher write the same `.cs`. Ticking one unticks the other.

## Windows

| OS | Python |
|---|---|
| Windows 7 SP1 | 2.7.18 or 3.8.10 |
| Windows 10 / 11 | 3.8–3.12 |

Add a pack in `grovekit/packs.py` → `catalog()`. See [docs/PACK_FORMAT.md](docs/PACK_FORMAT.md).

Related: [gta-sa-win7-mods](https://github.com/whirledclassic/gta-sa-win7-mods) · [sa-aw-fps](https://github.com/whirledclassic/sa-aw-fps)
