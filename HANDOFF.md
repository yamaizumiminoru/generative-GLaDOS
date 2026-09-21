# Handoff — 2026-09-21

## Agreed direction

Portal 2 campaign, original dialogue retained, action-driven GLaDOS with short generated voice remarks, no microphone. Local execution is the goal. One reliable room is the public PoC. Explicit hints are planned; the two-colour same-location gesture is an optional help request, not an automatic diagnosis of misunderstanding.

Read [docs/PLAN.md](docs/PLAN.md) first. Do not expand into whole-campaign support or a general AI-NPC framework before the single-room demonstration works.

## This checkpoint

- Re-read the repository baseline and actual placeholder bridge.
- Inspected the reference Windows hardware and installed map entity data without changing game files or saves.
- Chose `sp_a2_laser_intro` / `catcher_1` / `OnPowered` + `OnUnpowered` for the first actual gameplay signal.
- Added a small manual-attach VScript probe and a strictly framed, bounded Python log reader.
- Added ten Python reader tests and an explicitly synthetic replay fixture.
- Wrote the full plan, evidence/limitations, and the next live-test procedure.

## Evidence status

| Check | Status |
|---|---|
| Installed campaign map/entity presence | Observed by reading the actual local BSP entity lumps |
| Python reader tests | Passed in the isolated development container (10 tests) |
| Synthetic fixture -> CLI reader | Checked separately; not engine evidence |
| VScript syntax/runtime inside Portal 2 | NOT RUN |
| Game -> Python live events | NOT RUN |
| LLM generation / local simultaneous performance | NOT RUN |
| GLaDOS voice / original-dialogue synchronization | NOT RUN |
| Hint correctness / reusable installer | NOT IMPLEMENTED |

No model was downloaded, no paid API used, no service started, and no Portal installation file, save, key binding, or Steam launch option was changed. The game was not launched for this checkpoint. Hardware details in public findings are anonymized; do not publish account paths or save content.

## Next concrete action

Perform the protected M1 smoke test in [docs/PROBE.md](docs/PROBE.md). Confirm the installed build's actual script APIs, cheat requirements, console framing, receiver callbacks, duplicate-attach behavior, and cleanup. Fix the probe against real errors, not a mock. Only after a genuine `laser_powered`/`laser_unpowered` capture should M1 be marked complete.

In parallel with later M2 work, inspect and pin a minimal upstream TTS implementation. The full desktop assistant is not the integration target. Its README functionality is not proof of ready-to-run voice quality on this PC. A ready local model endpoint has not been confirmed.

## Reporting rules

Do not call the starter `bridge.py` generative: it returns deterministic placeholder text. Do not infer the current map from arbitrary strings in a save; use a live handshake. Do not interpret static scene counts as absence of dialogue. Do not claim invalid portal shots, deaths, gaze, novelty, or player confusion can already be observed.

No background work has been scheduled. Continue from the repository's actual current head on the next work turn; re-read files before changing them.
