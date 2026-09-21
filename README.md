# generative-GLaDOS

> What if the next generation of games wasn't about more pixels?

A proof of concept for connecting **Portal 2 game state** to a generative GLaDOS that can observe, remember, and react to the player's behaviour.

## Goal

Keep Portal 2's original campaign and canonical dialogue intact. Add short, supplementary GLaDOS remarks generated from what the player actually does.

The first milestone is deliberately small:

1. Portal 2 emits one structured gameplay event.
2. A local bridge receives it.
3. A generator produces one short GLaDOS-style reaction.
4. The reaction is returned for in-game playback.

No microphone or player dialogue is required.

## Design principles

- **Campaign first.** Test chambers are a development sandbox; the campaign is the showcase.
- **Do not replace canonical dialogue.** Generated remarks fill appropriate gaps.
- **Actions are the input.** GLaDOS reacts to gameplay, not player speech.
- **Silence matters.** Most events should produce no remark.
- **Memory matters.** Repetition and prior behaviour should change later reactions.
- **Hints should scaffold, not spoil.** A manual hint request may become progressively more explicit.
- **Game state beats vision.** Prefer structured engine state over screen recognition.
- **Local-first eventually.** The PoC may keep model/TTS backends swappable so local inference can be used.

## PoC event format

Example:

```json
{
  "event": "portal_attempt",
  "map": "example_map",
  "timestamp": 123.4,
  "details": {
    "valid_surface": false,
    "repeat_count": 3
  }
}
```

## Architecture

```text
Portal 2
   |
   | structured event
   v
Portal adapter  --->  event log / memory
   |
   v
Generative bridge
   |
   +--> response policy (speak or stay silent)
   |
   +--> LLM
   |
   +--> optional TTS
   |
   v
Portal 2 playback
```

## Status

🚧 Early proof of concept.

Current target: establish the round trip with a single campaign gameplay event before adding long-term memory, adaptive hints, or broad event coverage.

## Roadmap

- [ ] Receive a synthetic event in the bridge
- [ ] Generate a constrained one-line reaction
- [ ] Identify and capture one Portal 2 campaign event
- [ ] Return generated output to Portal 2
- [ ] Play generated audio in game
- [ ] Add repetition memory
- [ ] Add speech cooldown / salience policy
- [ ] Add manual adaptive hint command
- [ ] Package a reproducible campaign demo

## Legal / project scope

This is an independent fan-made research/prototyping project and is not affiliated with or endorsed by Valve.

Do not commit proprietary Portal 2 assets or extracted game audio to this repository. AI/TTS backends should remain replaceable; users are responsible for complying with the terms and licences of the models and assets they choose.
