# Prior-Art Research

- Researched at: 2026-08-04
- Queries: `script to explainer video agent skill`; `Remotion captions timeline skill`; `concept motion graphics workflow`; `video render quality audit skill`
- Catalogs: skills.sh and SkillsMP
- Runner: `research_prior_art.py`
- Catalog result: both catalogs completed for all four queries in the local run; full normalized output is `prior-art-candidates.json`.
- Rating evidence: unavailable. Install counts and repository stars remain separate adoption signals.

## Shortlist

| Candidate | Source | Relevance | Mechanism inspected | Decision |
|---|---|---|---|---|
| `remotion-captions` | [remotion-dev/skills](https://github.com/remotion-dev/skills/blob/f94c1e18db2bb30b904784b986f6897822b8f152/skills/remotion-captions/SKILL.md) | High for caption timing | Small root entrypoint, JSON caption objects with `startMs`/`endMs`, lazy-loaded task references | adapt |
| `hyperframes` | [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes/blob/77f95e46e038ee93e03b3f7a0099b25a4feb73f8/skills/hyperframes/SKILL.md) | High for routing and project state | State-based routing, one route contract, domain skills loaded on demand, brief as handoff artifact | adapt |
| `explainer-video` | [iart-ai/explainer-video-skills](https://github.com/iart-ai/explainer-video-skills/blob/3e2d411b725d9a72939cf8e5eb81579e751373e7/skills/explainer-video/SKILL.md) | High for script-to-screen structure | Explicit trigger examples, script/storyboard/narration/caption/render sequence, output contract and rendered-still checks | adapt |
| `explainer-video-review` | [same repository](../explainer-video-review/SKILL.md) | Internal companion | Four-dimensional post-render review and concrete issue output | keep as handoff target |

## Keep

- A concise root entrypoint with explicit trigger and exclusion boundaries.
- One canonical time representation for scenes and captions.
- Lazy resource routing by semantic topology.
- A rendered-output handoff that lists the files and evidence needed by the review stage.

## Adapt

- Remotion's caption object idea becomes frame-based `timeline.json` cues because the target Skill supports Remotion and HyperFrames.
- HyperFrames' state/brief separation becomes `segments.json`, `timeline.json`, and `production-handoff.json` without adopting HyperFrames as the default engine.
- iart's script-to-screen and rendered-still checks become a Chinese-first production contract; its fixed runtime, hardcoded pace, and two-line caption defaults are not copied.

## Reject

- A universal engine default: the target Skill keeps Remotion and HyperFrames as selectable adapters.
- A fixed 30–90 second story formula: the target workflow serves concept explainers with user- or script-defined length.
- A second post-render audit checklist inside the production entrypoint: the repository already has `explainer-video-review`.
- Popularity as quality proof: catalog installs and stars are retained as separate telemetry, not a combined score.

## Invent

- A half-open frame interval contract for `timeline.json`.
- A deterministic `validate_timeline.py` check for segment/cue ordering and cross-file IDs.
- Explicit `resource_status: pending` behavior for semantic topologies without an archived resource.
- A production-to-review handoff and full-rerender loop that keeps the collection's two Skills separate.

## Missing evidence

- No provider-backed full render was run by this refactor.
- No real MP4 playback or human blind review was recorded.
- The catalog search proves discovery coverage, not that the resulting Skill is superior to any candidate.