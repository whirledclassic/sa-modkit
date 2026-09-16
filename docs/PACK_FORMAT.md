# Adding a pack to SA Modkit

The engine is `grovekit/engine.py` → `catalog()`.

Each pack is a dict with `id`, `name`, `blurb`, `root`, `repo`, `files` (src, dest-under-GTA, keep_if_exists), `compile` (txt → CLEO\\file.cs), optional `min_source_bytes`.

Rules:
- Destinations stay under the game folder.
- If Sanny is missing the `.txt` is copied next to the intended `.cs`.
- Do not vendor `gta_sa.exe`, `.img`, `.ifp`, or ripped art.
- Document keys so two packs do not bind the same F-key.

Discovering the repo: add the folder to `discover_pack_roots()` (`../name`, `vendor/name`, `packs/name`).
