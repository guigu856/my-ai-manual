# Prior-art research

Research date: 2026-08-11

Source version: `dreammis/social-auto-upload@008e4ff66abdf48eb1f4b999272ef979711af436`

Public rating evidence: unavailable

## Candidates inspected

### `xiaohongshu-upload`

Source: <https://github.com/dreammis/social-auto-upload/tree/main/skills/xiaohongshu-upload>

- Keep: CLI-first `login → check → upload` flow and account alias isolation.
- Adapt: add UTF-8 file transport, dry-run, idempotency and online editor round-trip.
- Reject: treating `publish/success` as sufficient final evidence.

### `douyin-upload`

Source: <https://github.com/dreammis/social-auto-upload/tree/main/skills/douyin-upload>

- Keep: explicit split between video `title + desc + tags` and note `title + note + tags`.
- Adapt: represent the split as a platform-neutral adapter contract.
- Reject: marking the adapter operational before local submit and read-back evidence exists.

### `kuaishou-upload`

Source: <https://github.com/dreammis/social-auto-upload/tree/main/skills/kuaishou-upload>

- Keep: ordered real image files and no repeated-path shortcut.
- Adapt: move media uniqueness into the shared preflight.
- Reject: copying platform selectors into the core Skill.

### `bilibili-upload`

Source: <https://github.com/dreammis/social-auto-upload/tree/main/skills/bilibili-upload>

- Keep: required category `tid`, real-terminal login boundary and runtime-managed `biliup`.
- Adapt: model classification and interactive login as adapter-specific fields.
- Reject: a generic assumption that every login can run headlessly.

## Original contribution

- A cross-platform state machine that distinguishes `submitted` from `published-verified`.
- UTF-8 corruption gates based on strict decoding, CJK presence and suspicious question-mark runs.
- Stable publish intent IDs to block accidental duplicates.
- Online edit-page round-trip and same-post repair for Xiaohongshu notes.
- Explicit `validated` versus `reserved` adapter semantics.
