# generative-GLaDOS

> What if the next generation of games wasn't about more pixels?

An early proof-of-concept project connecting **Portal 2's observed game state** to a generative GLaDOS that can remember and react to the player's behavior.

**Status: engineering foundation, not yet a working generative-AI mod.** The original `bridge.py` is a deterministic placeholder. A real Portal 2 -> language model -> voice round trip has not yet been demonstrated.

## The intended experience

Keep the original single-player campaign and recorded dialogue. Add occasional, short, newly generated remarks about what the player actually did. No microphone or player dialogue. Add requested, progressively more specific hints only when they are grounded in verified room state.

One carefully integrated campaign room is the first release scope. The graphics and puzzle rules are unchanged.

## Start here

- [Implementation plan and acceptance gates](docs/PLAN.md)
- [Verified findings and unresolved assumptions](docs/FINDINGS.md)
- [Current handoff](HANDOFF.md)
- [Next live Portal 2 probe test](docs/PROBE.md)

The initial probe targets `catcher_1` in `sp_a2_laser_intro` and `sp_a2_laser_stairs`. It listens for receiver power changes; it does not claim to understand arbitrary player actions. Its engine runtime test is still pending.

## Run the dependency-free reader tests

Python 3.11 or later. Windows PowerShell, from the repository:

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
py -m unittest discover -s tests -v
py -m generative_glados.telemetry tests/fixtures/probe.synthetic.log
```

On Linux/macOS, use `PYTHONPATH=src python -m unittest discover -s tests -v`.

The replay is **synthetic**, labelled in every observation, and proves only the reader contract. For a live run and cleanup, follow the probe instructions rather than editing `mapspawn.nut` or global key bindings.

## Boundaries

Observe through small game-side hooks; reduce state and manage speech timing outside the engine; send bounded facts to a replaceable model; synthesize and play short responses only when permitted. The language model never gets arbitrary game-console or operating-system execution.

Local inference is the goal, not a measured achievement yet. The first voice experiment may play externally through the normal audio device; it must not be described as native Source audio injection. Original dialogue takes priority. Failure should make the added character quiet, not break the game.

## Dependencies and distribution

The [GLaDOS Personality Core](https://github.com/dnhkng/GLaDOS) is a candidate for narrow voice/backend reuse, not a Portal adapter already included here. No upstream code, model weights, Valve assets, or extracted audio are bundled at this checkpoint. Public-release licence choices and voice/model distribution checks remain on the release checklist.

This is an independent fan-made project, not affiliated with or endorsed by Valve. Do not commit proprietary game assets, personal saves, credentials, or raw personal logs.
