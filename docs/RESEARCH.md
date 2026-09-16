# Research log — what exists, what we will not copy, what we ship

Last pass: 2026-09-16.

## Already on this desk

| Pack | Hook | Status |
|---|---|---|
| GroveLink | **K** phone + LAN bridge `:8088` | shipping |
| Companion switcher | **H / J** | skin ships; full body still a stub |
| SA-AW FPS | **F4** exo layer | shipping on enhance branch |
| SA Modkit | destination picker, **opt-in** packs | 0.1.1 |
| **GroveCast** | **F3** slate + OBS `:8099` | new this pass |

## What the public SA scene already did

- Trainers, chaos / Twitch Plays, wanted-level buttons, car spawners.
- Gon_iss Interactive Phone (2014–15) and Phone Mod 2 — taxis, contacts, in-game apps. No OBS feed.
- MixSets / SilentPatch / ModLoader / CLEO 4–5 — infrastructure, not streamer tools.
- Static “GTA-look” Twitch overlays (Shark Stack, StreamDPS). PNG frames. They do not read the 2005 game.
- Kreyg, September 2026: viewers spend **Twitch bits** to TTS-call CJ via plugin-sdk + a private C# app. Viral. **Not released.** Dexerto 2026-09-05.

## What we will not clone

- Bits-to-TTS incoming calls. That is Kreyg’s bit.
- Generic chaos wheels and “spawn a Rhino” redeem menus.
- Ripped CoD / GTA V HUD art.
- Anything that needs CLEO+ only. Floor stays CLEO 4.4 + Windows 7.

## Gap we can own

Nobody ships a plug-and-play OBS lower-third that reads a 1.0 CLEO install and sits next to an existing LAN phone.

GroveCast writes `cast.ini`. OBS polls `http://127.0.0.1:8099/obs`. Streamer presses **F3** when they want the slate hot. Chat does not get a red button.

## Next originals (not started)

1. Pager, not chaos — reuse GroveLink RING so a viewer on the same Wi-Fi can page CJ. Name on the slate. No bits, no TTS steal.
2. Companion bug — when the full switcher is real, overlay shows the homie model id.
3. Seed card — one number on the slate so a later fair-play event pack can be replayed.
4. Director hold — F3 long-press freezes the last zone name for a talking-head beat.

## Keys (do not collide)

| Key | Owner |
|---|---|
| K | GroveLink |
| H J (F6 G N B) | switcher |
| F4 8 9 0 | AW FPS |
| F3 | GroveCast |
