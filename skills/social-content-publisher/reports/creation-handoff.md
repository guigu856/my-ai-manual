# Creation handoff

## Result

- Skill: `social-content-publisher` 0.1.0
- Job: publish completed social media packages and verify the online result.
- Current evidence: Xiaohongshu static note only.

## Reference skills studied

- `xiaohongshu-upload`: CLI-first auth and upload contract; extended with round-trip verification.
- `douyin-upload`: note / video metadata split; mapped into reserved adapter fields.
- `kuaishou-upload`: unique ordered images; promoted into common preflight.
- `bilibili-upload`: category and interactive login boundaries; kept adapter-specific.

All candidates came from `dreammis/social-auto-upload@008e4ff6`; public rating evidence is unavailable.

## Absorbed and rejected

- Keep: explicit `login`, `check`, `upload-note` and `upload-video` operations.
- Adapt: one platform-neutral manifest and one gate ladder.
- Reject: success-message-only acceptance and unsupported-platform claims.
- Invent: UTF-8 / CJK corruption detection, publish intent ID, online editor read-back, same-note repair and adapter maturity labels.

## Advantages and evidence

- **Design advantage**: submission and content correctness are separate states; see `SKILL.md` and `references/workflow-and-gates.md`.
- **Validated advantage**: the local Xiaohongshu fixture exposed and repaired a real `?AI????` corruption path; regression tests cover that signature.
- **Design advantage**: unimplemented platforms have named adapter slots without empty files or false support claims.
- **Hypothesis**: the shared adapter contract should reduce future platform integration drift; provider-backed multi-platform evidence is missing.

## Verification and limits

- Unit tests cover UTF-8 preflight, title truncation, reserved adapters and redacted dry-run summaries.
- Trigger cases cover publish, verify, repair, near-neighbor production and non-publishing requests.
- Local Xiaohongshu publish and repair evidence exists from 2026-08-11.
- Douyin, Kuaishou, Bilibili, Tencent and YouTube remain `missing evidence`.
- Deletion automation is deliberately excluded from 0.1.0.
