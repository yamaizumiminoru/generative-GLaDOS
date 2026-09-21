# Technical findings and evidence

Checked 2026-09-21. Statements below distinguish observed files, upstream documentation, and pending runtime work. No game assets or personal save files are included here.

## Repository baseline

The starting `main` commit was `0c21458314097c15309461c69d228b29cf95ed14`. It had a README, Python packaging, a deterministic stdin/stdout placeholder bridge, and one placeholder-contract test. There was no Portal integration, LLM, TTS, or live capture. Keep this distinction in future progress reports.

## Reference machine (read-only inspection)

Windows; Intel Core i7-1355U; Intel Iris Xe integrated graphics; approximately 32 GB RAM (31.6 GiB reported); Python 3.13 installed. Portal 2 had already been played successfully by the user. The inspected Steam app manifest reported build `23973718`.

An Ollama executable was present, but the default `127.0.0.1:11434` endpoint did not respond during inspection. No model was verified ready. This is not proof that no models exist at a custom location. No inference benchmark has been run, no model downloaded, and no cloud credentials inspected or used.

Game files and saves were read but not altered, and the game was not launched or closed. Public documentation intentionally omits usernames, full save paths, account identifiers, and save content.

## Installed campaign BSPs

Read the entity lump directly from the user's installed, unmodified maps. These are **static entity counts**, not a complete runtime inventory.

| Map | Total entities | Laser emitters | Laser catchers | Weighted cubes | Floor buttons | Static choreographed scenes |
|---|---:|---:|---:|---:|---:|---:|
| `sp_a2_laser_intro` | 376 | 1 | 1 | 0 | 0 | 1 |
| `sp_a2_laser_stairs` | 610 | 1 | 1 | 1 | 1 | 0 |

Both maps contain `prop_laser_catcher` / `catcher_1` and authored `OnPowered`/`OnUnpowered` output entries. `sp_a2_laser_stairs` also contains `prop_floor_button` / `exit_button-button`, with `OnPressed`/`OnUnPressed`, and `prop_weighted_cube` / `cube_dropper_01-cube_dropper_box`, with an authored `OnFizzled` entry.

This supports the selection of a first observation hook. It does **not** prove that `ConnectOutput` has been tested in the installed game, that every runtime object retains the same identity after respawn, or that receiver power alone describes puzzle completion. Output lists can contain duplicate keys; the quick inspection used for candidate selection was not a complete puzzle-logic extraction.

Do not infer the player's current room by searching a save for arbitrary map-name strings. The inspected saves also contained cross-campaign script strings. The live `GetMapName()` handshake remains the source for the current loaded room.

## Source/VScript integration

The [Valve Developer Community VScript fundamentals](https://developer.valvesoftware.com/wiki/VScript_Fundamentals) document `script_execute`, script scopes, entity lookup, and `ConnectOutput`. They also note that `mapspawn.nut` runs before entities exist. The installed `mapspawn.nut` itself describes being called on new game/transitions.

The [ppmod author documentation](https://github.com/p2r3/ppmod) describes map/load helpers, entity outputs, and player interfaces. It also documents caveats around loading into an already populated environment and saving during asynchronous functions. Therefore ppmod is an evaluated candidate, **not an unconditionally installed dependency**, and the first probe uses a very small vanilla script instead.

The [developer-console documentation](https://developer.valvesoftware.com/wiki/Developer_console) describes console logging. The exact prefix/flush behavior of `printl` through `con_logfile` and the command's cheat gating on the installed build still need a live test.

Several Portal-specific API pages returned access errors during web research. Do not claim those inaccessible pages were checked. Runtime feature guards and the first smoke test are required.

## Existing generative GLaDOS project

The current [dnhkng/GLaDOS README](https://github.com/dnhkng/GLaDOS) documents a broad assistant, including proactive behavior and an LLM/voice pipeline, plus a TTS API route. This is promising reuse material, not a ready Portal 2 adapter.

Its [pyproject.toml](https://github.com/dnhkng/GLaDOS/blob/main/pyproject.toml) specifies Python >=3.12 and separate CPU/GPU ONNX runtime extras. It also includes substantial desktop-assistant dependencies. Keep its runtime separate from our dependency-free observation reader.

The repository's [LICENSE.txt](https://github.com/dnhkng/GLaDOS/blob/main/LICENSE.txt) identifies an MIT code licence. Model weights, voice assets, training sources, and redistribution conditions require separate checking. No upstream code or weights have been copied into this repository in this checkpoint.

Earlier conversational estimates such as “70–80% already done” are not effort estimates to use for scheduling. Reuse can save voice/model plumbing; observation semantics, synchronization, grounded hints, and packaging remain our work. The actual TTS voice, startup behavior, and performance have not been verified here.

## Local model interface

[Ollama's chat API](https://docs.ollama.com/api/chat) documents structured output, streaming control, generation timings, and model keep-alive settings. These are suitable surfaces for a small adapter and a repeatable benchmark. No particular model or latency figure has been validated on the reference machine.
