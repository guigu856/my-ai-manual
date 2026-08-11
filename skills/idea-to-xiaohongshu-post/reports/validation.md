# Validation

- Checked at: 2026-08-11
- Package: `idea-to-xiaohongshu-post` 0.1.0

## Skill package

```text
validate_skill.py: PASS
failures: 0
warnings: 0
```

## Trigger boundary

```text
total: 15
passed: 15
false positive: 0
false negative: 0
pass rate: 1.0
```

Evidence: `reports/trigger-eval.json`

## Deterministic validator

```text
python -m unittest discover -s tests -p "test_*.py"
Ran 3 tests
OK
```

Covered cases:

- valid package passes
- wrong PNG dimensions fail
- missing `post.md` fails

## Real package runtime

The validator ran against the previously rendered 9-card AI whetstone carousel:

```text
PASS P16: package structure and 9 PNG cards passed
```

Evidence: `reports/real-package-validation.json`

This proves package parsing, 1080×1440 PNG inspection, contiguous filenames, title/body presence and contact-sheet discovery. It does not prove that a future agent run will produce persuasive content.

## Discovery and isolated install

- `npx skills add . --list`: detected the repository's 5 Skills, including `idea-to-xiaohongshu-post`.
- Isolated `--copy` install into a temporary HOME: PASS; root `SKILL.md` and all declared resources were present.

## Local release readiness

```text
pass: 6
warn: 3
block: 0
```

Warnings are expected before publication:

- working tree was dirty during local development
- merged-default-branch clean install remains pending
- provider-backed or human-blind output evidence remains missing

## Missing evidence

- provider-backed multi-topic output evaluation
- human blind review
- merged-default-branch remote install
- real Xiaohongshu publish metrics
