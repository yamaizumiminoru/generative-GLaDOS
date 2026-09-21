# Generative GLaDOS: implementation plan

Decision date: 2026-09-21. This is the working plan, not a claim that the mod is complete.

## 1. The product we are building

A small, reproducible Portal 2 **single-player campaign** demonstration in which GLaDOS notices an observed action, remembers relevant earlier actions, and delivers a newly generated, short, in-character remark. The original story and recorded dialogue stay intact. One carefully integrated room is the release scope; covering the entire campaign is not.

The first public demonstration must show a difference between two real play histories, not merely insert a random insult. A successful clip shows the action, its timestamped observation, the actual model response, and the audible result. Synthetic input, deterministic placeholder text, and prerecorded demonstration audio must be clearly labelled and must never be presented as live generation.

The player does not need to remember the campaign, identify events, learn modding, or speak into a microphone. The developer chooses and instruments the room; the player supplies normal play and a short acceptance check.

## 2. Non-negotiable scope

- No microphone, speech recognition, camera, or continuous screenshot interpretation.
- Preserve canonical dialogue and puzzle rules. No AI-directed entity manipulation.
- No new textures, maps, models, or copied Valve dialogue/audio in the repository.
- Local inference is the target. Cloud use is an explicit, separately configured alternative, never a silent fallback or an automatic paid request.
- Keep observation, memory, generation, speech scheduling, and audio playback separate.
- Do not run the full upstream desktop assistant with its unrelated autonomous agents or operating-system tools.
- Hints are requested, not forced on a player merely because they are experimenting.
- No API keys, personal paths, raw save files, or full console logs in public commits.

## 3. First room and first real event

**Instrumentation target: `sp_a2_laser_intro`.** The installed map contains a `prop_laser_catcher` named `catcher_1` with `OnPowered` and `OnUnpowered` outputs. That gives a concrete first gameplay signal: the receiver gains or loses laser power. It does not establish why the player acted, whether a shot missed, or whether the whole puzzle is solved.

**Showcase candidate: `sp_a2_laser_stairs`.** Its installed map also contains `catcher_1`, plus a weighted cube and a floor button. It offers more observable actions without committing to a complex later chapter. Use it only after checking live dialogue and actual puzzle dependencies. See [FINDINGS.md](FINDINGS.md).

The simpler room is a technical test, not an excuse to manufacture a dramatic demonstration. If the first room already produces interesting interactions, it may also become the showcase. Do not require the player to advance farther just to discover a map name; the developer can inspect files and use a protected development session.

## 4. Architecture and authority boundaries

```text
Portal 2: bounded VScript observation hooks
    -> framed observations in the local console log (first transport)
    -> Python reader + schema validation
    -> state reducer / small event memory / per-room progression adapter
    -> deterministic eligibility and dialogue-priority checks
    -> bounded context -> local language model -> validated short text
    -> speech synthesis -> cancellable playback / visible diagnostic transcript
```

**The model chooses phrasing, not game truth.** Counters, current receiver state, room identity, hint level, and eligibility come from code. Unknown values remain unknown. Absence of an observed event does not prove that the player did not perform an action before the observer attached.

Classify context as observed, derived, or uncertain. Do not turn “the player returned here” into “the player is confused,” or “the laser is powered” into “the puzzle is solved.” Initially do not claim the player looked at something, intentionally failed, used a novel solution, or missed a portalable surface: none of those detectors has been verified.

The language model gets no shell, game console, file-system, or MCP tool authority. Never evaluate generated text as VScript or insert it into an unrestricted console command. Future in-engine text/audio sinks must escape their inputs and allow only fixed operations.

### Transport decision

Start with `printl` -> local log -> Python. It avoids an unauthenticated remote-console service and a native binary plugin while testing the first observation. This is not an assertion that VScript offers general HTTP/file APIs or that the log is lossless.

The diagnostic probe is manually attached after map load, not injected through a replacement `mapspawn.nut`. It reports `bridge_attached`, not a fictional `map_loaded` or `player_spawned` event. Reload handling and automatic attach belong in M2.

If the measured log transport is unreliable, investigate a maintained plugin or loopback console bridge with strict command allowlisting. Change transport only for a demonstrated blocker. Do not begin by hooking engine memory.

### Audio decision

For the first audible demonstration, use an external, cancellable audio player sharing the normal output device. GLaDOS's voice does not need spatial positioning for this limited experiment. Label this accurately: audio played during the game, not already injected into the Source sound system.

This removes dynamic sound precaching/cache invalidation from the critical path. Source-native playback and integrated captions are a later improvement, unless external playback proves inadequate. Pause/load and original-dialogue priority are still mandatory even for external playback.

## 5. Milestones and exit criteria

### M0 — Grounded plan and baseline (current planning checkpoint)

Inspect the repository, installed game, target maps, and upstream integration surface. Record facts separately from assumptions. Create the smallest observation probe and a bounded reader; do not install large models or silently alter the running game.

**Exit:** plan and handoff committed; observed map/entity identifiers recorded; Python parser tested; live-engine status explicitly marked pending. This is not a completed AI PoC.

### M1 — One real observation out of Portal 2

Back up the save/config directories before a development run. Install only two uniquely named diagnostic files, after checking they do not already exist. Enable console logging explicitly, preserving its previous setting. Run the probe in a fully loaded supported room and exercise the receiver.

**Exit:** an actual game-produced `bridge_attached`, followed by `laser_powered` and `laser_unpowered`, reaches Python; original puzzle behavior still works. Attach twice, stop, and reload once. Missing events or unsupported commands are failures, not replaced with synthetic evidence.

`script_execute`/`script` cheat gating on the installed build must be checked. Never enable `sv_cheats` silently. Use a backed-up development session if required, and do not promise achievement compatibility before testing it.

### M2 — Trustworthy observation, memory, and silence

Add a reducer with `(run_id, seq)` deduplication/gap checks, map/reload epochs, bounded history, and a room-specific state model. Later snapshots reconcile state after load. Record actual entity outputs; add cube/button events only after independently confirming them.

Establish a reliable canonical-dialogue busy signal for the chosen room. A count of static `logic_choreographed_scene` entities is not such a signal: scenes may be created dynamically. Unknown speech status means no autonomous generated speech. A validated room-specific quiet window is an acceptable first implementation.

Add cooldown, expiry, single-flight generation, and a queue of at most one pending remark. Invalidate work on pause/load/map change and when its factual premise ceases to hold. Do not play an old remark just because synthesis finally finished.

**Exit:** replaying captured histories gives correct counts and eligibility decisions; repeated attach/reload does not multiply events; canonical speech is never deliberately interrupted; intentional experimentation is not automatically called failure. A fixed test sentence may check the audio plumbing, but is not presented as AI output.

### M3 — A real generated voice reaction

Evaluate a small local model against captured, labelled observations. Use a short prompt, a bounded output, one inference at a time, and no background agents. Start with one or two English sentences, approximately 35 words maximum. The event/action is chosen by the policy; the LLM supplies the phrasing.

Reuse the upstream GLaDOS TTS interface where verified, preferably as a persistent service rather than launching and loading it anew for every sentence. First verify that the selected backend actually produces the desired voice; an example request containing `voice: glados` is not sufficient proof of voice quality or model availability.

Benchmark Portal 2 alone, the model alone, TTS alone, and all together on the actual reference PC. Record latency, peak memory, and gameplay frame-time impact. Portal 2 running well does not establish simultaneous inference headroom.

**Exit:** a real action produces a newly generated, grounded, audible response; changing the prior play history changes the response appropriately; model/service failure leaves the game playable and GLaDOS silent. Label model identity, local/cloud execution, and audio route in the demo.

### M4 — Explicit, grounded hints in one room

Provide a normal hint key/command first. The two-colour, same-location portal gesture is a proposed alternative **request signal**, not proof that the player misunderstands portals. Verify actual portal-placement/shot behavior and accidental-trigger frequency before implementing it. Do not rely on two active portals coexisting at the same coordinates.

Author and verify a small room progression graph and three hint levels: draw attention, explain a relevant relation, then give a concrete next action. Select the valid hint from the real state; let the LLM phrase it. Gate spoilers in code, not only in the prompt. Advance levels only on a fresh request without intervening progress; reset after progress. With insufficient state, give no invented solution.

**Exit:** hints remain correct across relevant partial solutions, reloads, and repeated requests. The first hint does not unnecessarily reveal the full solution. The player can decline help and continue experimenting.

### M5 — A reproducible public PoC

Package a reversible install/uninstall path, pinned dependencies, model setup instructions, a clean-machine checklist, opt-in local logs, and an obvious stop/mute control. Separate original code from upstream dependencies and model/voice assets. Resolve licences and distribution terms before bundling any weights or audio. Merely linking to an upstream project is not a completed rights audit.

Record an uncut short demonstration plus a technical explanation. Make the event adapter reusable without building a general-purpose multi-game platform. Publish documentation for adding another room and substituting an LLM or TTS backend. Outreach to Portal modders and upstream contributors is a later action, not performed by this planning commit.

**Exit:** a second installation reproduces the experience; normal play and removal work; limitations are documented; synthetic fixtures are clearly distinguished from live evidence. No “world first” claim without a separate, supportable review.

## 6. Initial budgets (targets, not measurements)

- Prefer output callbacks to scanning every entity every frame. Begin any reconciliation polling at about 2 Hz and measure it.
- At most one generation and one pending remark. Initial autonomous cooldown: 30 seconds.
- Aim for a short observation-to-audio delay; provisional target is about 3 seconds median and 5 seconds at the 95th percentile when not blocked by original dialogue. Expire ordinary event remarks after about 5 seconds; hints have a separately measured deadline.
- Do not meet a latency target by reducing the game's responsiveness. Establish a repeatable baseline and agree a frame-time budget from measurements.
- Keep recent structured history small. Add SQLite only when persistence is useful; no vector database, multi-agent memory system, or full transcript in every prompt by default.
- Preserve account-independent history explicitly: attempts may remain in memory across a death, while puzzle state must reset to the loaded state. Do not merge play sessions merely because map names match.

## 7. Critical risks and fallbacks

| Risk | Response |
|---|---|
| An engine API/output does not work as documented | Capture the actual console error and change the probe; never simulate a passing integration test. |
| Console logging drops/changes records | Record sequence gaps and test flush latency; replace transport if measured behavior requires it. |
| Original dialogue overlaps generated audio | Fail silent; validate a room-specific signal before widening coverage. |
| Local LLM + voice is too slow on integrated graphics | Shorten context/output; use a smaller model and CPU scheduling; measure. Cloud is separately opted in, not automatic. |
| “GLaDOS voice” backend is unavailable or unsuitable | Report a text-only engineering checkpoint honestly; evaluate another permitted voice without mislabelling it as the final experience. |
| Portal-overlap gesture is ambiguous | Ship the ordinary hint command first. The gesture is not a release blocker. |
| Upstream assistant has too many dependencies | Integrate only the narrow TTS/backend surface; avoid its microphone/camera/autonomous tool stack. |
| Generated remark invents events or spoils the room | Restrict supplied facts and allowed hint content; reject bad output and remain silent. Test semantics, not just JSON. |
| Save/load serializes temporary hooks unexpectedly | Back up first; test a dedicated development save; do not install a global auto-loader prematurely. |

## 8. What is deliberately postponed

Whole-campaign support, voice conversation, a general world model, screen vision, self-modifying puzzles, learning bosses, Wheatley/Navi ports, persistent emotional agents, Steam Workshop packaging, and promotional posting. These can follow a compelling, reliable single-room experience.

## 9. How progress is reported

Each checkpoint states: code written; tests actually run; live behaviors observed; remaining blockers; the next concrete action. A passing parser suite is not proof that Portal 2 is connected, and audible placeholder audio is not proof of generation. The meaningful acceptance test is the player experiencing the complete loop.
