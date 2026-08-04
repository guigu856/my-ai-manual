---
name: explainer-video-review
description: |
  Use this Agent Skill when a user provides an existing rendered MP4 or concept-motion explainer video and asks for a post-render audit, frame-based review, subtitle check, visual-quality review, spatial-continuity review, or audio-sync review. It checks visual expression, spatial continuity, temporal alignment, subtitles, and delivery integrity, then produces evidence-linked findings and a repair handoff. Trigger on requests such as “审查这个解说视频成片”“检查字幕和音画同步”“逐帧找出动效问题”。Exclude script-only rewriting, new video production, existing-footage editing, reference-video study, and generic media recommendations; route production to `script-to-explainer-video` and reference study to the repository's reference-study Skill.
metadata:
  author: guigu856
  version: "1.1.0"
---

# 概念动效视频成片审查 Skill

## 职责边界

本 Skill 负责对已经渲染的口播或概念动效视频做 post-render audit：

- 建立审查基准、媒体清单和可复现的抽样计划
- 先做媒体、字幕、时间轴和音频的结构检查，再做画面与声音审查
- 按视觉表达、空间连续、时序对齐、字幕可读性四个维度记录证据链
- 输出带时间戳、证据引用、严重级和修复建议的问题报告
- 将需要源文件修复的问题交给 `../script-to-explainer-video/SKILL.md`，修复后整片重渲染并复审

审查阶段保持源文件和成片只读；用户明确要求执行修复时，仍沿用生产 Skill 的时间轴契约，不在本 Skill 内另造制作流程。

## 输入与输出

最低输入：

- 已渲染 MP4 或可读取的成片视频

推荐输入：

- 冻结文稿或 `segments.json`
- `timeline.json`、字幕文件、最终配音
- 制作要求、平台规格、目标比例和用户重点关注项

输出：

- `review-manifest.json`：媒体指纹、规格、基准、采样计划和证据范围
- `review-report.json`：摘要、四维结果、问题清单、严重级和复核状态
- 可读 Markdown 问题清单或聊天内摘要
- 源文件修复、整片重渲染和复审的交接说明

缺失的冻结文稿、时间轴、原始音频或人审结果写入 `missing_evidence`，不用推测结果填补证据空洞。

## Router Rules

- Trigger when an existing MP4 or rendered explainer video needs a post-render audit, quality review, subtitle review, frame review, or audio-sync review.
- Use the four review dimensions and return evidence-linked findings; a report is the primary deliverable.
- Route new script-to-video production to `../script-to-explainer-video/SKILL.md`.
- Route reference-video learning, shot breakdown, and editing-grammar extraction to the repository's reference-study Skill.
- Exclude script-only rewriting, caption-only generation without a video review, existing-footage editing, and generic media advice.

## Compact Workflow

1. Inventory the MP4, available frozen sources, requirements, and tool availability.
2. Generate a deterministic sampling plan; use quick, standard, or dense review based on duration and motion density.
3. Run structural preflight for media metadata, audio presence, subtitle coverage, timeline alignment, and render integrity.
4. Review visual expression, spatial continuity, temporal alignment, and subtitle readability against the same evidence bundle.
5. Record findings with timestamps, evidence references, severity, confidence, and repair scope.
6. Return one complete report; group fixable source defects into a repair handoff and request a new full render for re-review.

## Gate Ladder

- **Input gate**: the MP4 is readable and the review basis is recorded; missing artifacts receive an evidence label.
- **Media gate**: duration, frame rate, dimensions, stream presence, and audio state are recorded.
- **Evidence gate**: every finding points to a timestamp, frame, audio window, subtitle cue, or source artifact.
- **Dimension gate**: all four dimensions are reviewed or explicitly marked `missing_evidence`.
- **Triage gate**: each finding has severity, confidence, repair scope, and pass/warn/fail status.
- **Handoff gate**: source defects point back to the production Skill; a repaired source requires full rerender and a new report.

## Output Contract

- `review-report.json` and the human-readable report use the same finding IDs, timestamps, severity, status, and evidence references.
- Status values are `pass`, `warn`, `fail`, and `missing_evidence`; severity values are `blocker`, `major`, `minor`, and `note`.
- A finding without a concrete evidence reference remains a hypothesis and keeps that label until evidence is attached.
- A complete pass requires media preflight, four dimension results, and a recorded output/review evidence boundary.
- Provider playback, human perception, and external render evidence remain `missing_evidence` until observed.

## 审查维度

- [审查契约、报告和状态](references/review-contract.md)
- [采样策略与证据链](references/sampling-and-evidence.md)
- [四维检查规则](references/four-dimensions.md)
- [修复交接与复审循环](references/repair-handoff.md)

## 默认参数

| 参数 | 默认值 | 覆盖条件 |
|---|---|---|
| 审查档位 | standard | 用户指定 quick 或密集动效、转场、快速字幕时覆盖 |
| 初始采样 | 1s/帧或每段首中尾 | 动效密集段加密到 0.25–0.5s/帧 |
| 音频核对 | 每个高风险 cue 前后各 1s | 音画同步问题或用户指定区间覆盖 |
| 手机可读性 | 约 360px 宽等效检查 | 平台指定画布和安全区优先 |
| 报告方式 | Markdown 摘要 + JSON 证据 | 长片或自动化复核时保留完整 JSON |

## 资源与验证

- 报告校验：`python scripts/validate_review_report.py --input <review-report.json>`
- 采样计划：`python scripts/build_sample_plan.py --duration <seconds> --preset standard`
- 触发回归：`python C:/Users/32249/.codex/skills/qiaomu-meta-skill/scripts/trigger_eval.py . --cases evals/trigger_cases.json`
- 包校验：`python C:/Users/32249/.codex/skills/qiaomu-meta-skill/scripts/validate_skill.py .`

## 完成条件

- 媒体规格和审查基准已经记录
- 抽样计划可复现，所有发现都有证据引用或明确标记为 `missing_evidence`
- 四个维度均有结果，严重级和修复范围清楚
- 报告通过结构校验，交接对象和复审条件明确
- 成片修复后使用新版本整片复渲，并重新生成报告
