# M1 diagnostic probe: operator instructions

**Engineering probe, not a playable generative-AI mod.** Its VScript has not yet been executed in Portal 2. The Python reader has been tested on synthetic records only. This procedure is the next live validation, not a record of a completed validation.

## Before the live test

Use a backed-up development session. While the game is closed, back up its save and configuration directories outside the game installation. Record any existing console logging setting. Do not overwrite the user's normal save or assume achievements remain enabled with development commands.

From a fresh checkout, copy only these two files to their matching paths below the installed `portal2` game directory:

```text
portal2/cfg/generative_glados_probe.cfg
portal2/scripts/vscripts/generative_glados/probe.nut
```

Check for existing files first; if either exists, stop and compare rather than overwrite. Do not replace `mapspawn.nut`, `autoexec.cfg`, `config.cfg`, `gameinfo.txt`, any BSP, or any Valve script. No DLL injection, background service, or new network listener is required.

## Reader (Windows PowerShell, from the repository)

```powershell
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
py -m generative_glados.telemetry 'C:\Program Files (x86)\Steam\steamapps\common\Portal 2\portal2\generative_glados.log' --follow
```

The log path may differ for another Steam library. The reader waits if the file does not exist yet. Use a fresh log or `--from-end` for a live run; otherwise historical records are replayed. It only prints validated JSON observations. It does not call the placeholder bridge, an LLM, or TTS.

## Game-side procedure

Load the development room fully before attaching. `sp_a2_laser_intro` is the first target. The developer may use `map sp_a2_laser_intro` in a protected test session; that is not permission to replace the user's normal progression. `sp_a2_laser_stairs` is a second supported observation target.

In the developer console, query `con_logfile` and record the previous value. Then:

```text
con_logfile generative_glados.log
exec generative_glados_probe
```

If Portal reports that a command needs cheats, stop and record the error. This project does not silently issue `sv_cheats 1`. A developer can explicitly choose a backed-up cheat-enabled session, but achievement/save implications are not certified here.

Expected **real** first record: `event: bridge_attached`, `origin: engine`, the actual map name, and `data.laser_hook: true`. This is an attach acknowledgement, not evidence that a puzzle event occurred. On another map the script may emit a handshake with `laser_hook: false`; that is not M1 success.

Operate the receiver, then remove its power. Expected records: `laser_powered` and `laser_unpowered`, with increasing sequence numbers and observed game times. Preserve a short local recording/log that shows the game action and observation together.

Optional command-path checks:

```text
script GGProbe.Hint()
script GGProbe.Stop()
```

The first records an explicit request only; **it does not give a hint yet**. The second disables subsequent observation callbacks. It does not mutate the laser or prevent original map outputs. Reload the map to replace a probe; repeated attachment deliberately refuses to duplicate callbacks.

## Cleanup

Restore the exact previous `con_logfile` setting, then exit the game. Remove only the two files copied by this procedure. A stop flag is not equivalent to unloading saved script state: do not reuse a development save containing hooks as an unmodified baseline. Restore/use the pre-test baseline for clean-play comparisons.

## Acceptance record

Record game build, room, whether cheats were needed, actual output prefix, observed latency, duplicate-attach behavior, stop behavior, and normal puzzle operation. A new-map load and a saved-game load must eventually be tested separately. The diagnostic reader does not yet reconstruct exactly-once state across reloads.

Do not report M1 complete from `tests/fixtures/probe.synthetic.log`. That file exists to test parsing and carries `origin: synthetic` on every record.
