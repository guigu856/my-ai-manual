# Creation Handoff

## Result

- Skill: `script-to-explainer-video`
- Version: `1.3.0`
- Job: turn spoken scripts or concept briefs into audio-driven concept-motion explainer videos
- Repository role: one Skill inside the `my-ai-manual` collection; repository-level Rules and other Agent materials remain outside this package boundary
- Publication status: local feature branch; remote PR is not part of this validation pass

## Reference skills studied

- `remotion-captions`: adopted a lean root entrypoint and structured caption timing; adapted milliseconds to the target frame-based timeline.
- `hyperframes`: adopted state-based routing and explicit project handoff; kept Remotion and HyperFrames as selectable adapters.
- `explainer-video`: adopted explicit trigger examples, script-to-screen sequencing, output contracts and rendered-still checks; kept its fixed runtime and caption defaults out of this package.
- `explainer-video-review`: retained as the existing repository companion for post-render inspection rather than duplicating its checklist.

## Absorbed and rejected

- Keep: audio as the main clock, semantic motion resources, exact voiceover text in captions, and source-fix → full-rerender → recheck.
- Adapt: resource routing, timeline representation, engine selection, defaults, and output handoff.
- Reject: repository Rules as an implicit package dependency, universal engine selection, unverified quality claims, and a second audit Skill inside production.
- Invent: half-open frame contract, deterministic timeline validator, resource pending status, and explicit companion handoff.

## Advantages and highlights

- [design advantage] The root Skill separates role, input/output contract, workflow, resource routing, and companion handoff.
- [design advantage] The collection-repository boundary is explicit; this package does not require the repository's unrelated Rules or other Agent materials.
- [validated advantage] `validate_skill.py` passed with zero failures and zero warnings.
- [validated advantage] Trigger evaluation passed 11/11 cases with zero false positives and zero false negatives.
- [validated advantage] Timeline fixtures passed: a valid timeline exited 0, an overlapping cue exited 2, and two unit tests passed.
- [hypothesis] The new contract should reduce timeline drift and accidental triggering, but real provider-backed render and human review evidence is missing.

## Verification and limits

- Package validation: pass.
- Trigger evaluation: 11/11 pass.
- Local release gate: pass, with warnings for dirty development worktree, clean public install, and provider/human output evidence.
- Missing evidence: real render, playback, human review, and public clean installation.
- Permissions: repository Rules and the companion review Skill were not changed; no merge or public release is claimed.