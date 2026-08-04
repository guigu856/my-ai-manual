# 审查契约、报告和状态

## 1. 角色

本 Skill 是成片交付后的审查层。它读取已经渲染的媒体和冻结基准，生成可复核的结果；生产 Skill 负责源文件、配音、时间轴和整片重渲染。

## 2. 输入优先级

按以下顺序建立审查基准：

1. 用户明确给出的制作要求、版本号和重点问题
2. 与 MP4 版本匹配的 `timeline.json`、`segments.json`、字幕和配音
3. 当前工程中的冻结产物和渲染清单
4. 视频自身可观察内容

当高优先级基准缺失时，报告仍可继续，但要在 `evidence_boundary.missing_evidence` 中记录缺口，并降低结论的置信度。

## 3. `review-manifest.json`

```json
{
  "schema_version": "1.0",
  "skill": "explainer-video-review",
  "run_id": "review-20260805-001",
  "media": {
    "path": "renders/final.mp4",
    "sha256": "SHA256",
    "duration_s": 42.8,
    "fps": 30,
    "width": 1920,
    "height": 1080,
    "audio_streams": 1
  },
  "basis": {
    "segments": "segments.json",
    "timeline": "timeline.json",
    "captions": "captions.srt",
    "audio": "audio/narration.wav",
    "requirements": "requirements.md"
  },
  "sampling": {
    "preset": "standard",
    "interval_s": 1.0,
    "timestamps_s": [0.0, 1.0, 2.0, 12.5, 42.79]
  },
  "evidence_boundary": {
    "observed": ["media_metadata", "sampled_frames"],
    "missing_evidence": ["human_playback_review"]
  }
}
```

## 4. `review-report.json`

报告至少包含：

- `overall.status`、`overall.severity`、`overall.confidence`
- 四个 `dimensions`：`visual_expression`、`spatial_continuity`、`temporal_alignment`、`subtitle_readability`
- `findings[]`：每个问题一个稳定 ID
- `handoff`：源文件修复、整片重渲染和复审条件
- `evidence_boundary`：已观察证据和缺失证据

问题对象使用以下形状：

```json
{
  "id": "T-003",
  "dimension": "temporal_alignment",
  "status": "fail",
  "severity": "major",
  "confidence": "high",
  "start_s": 12.40,
  "end_s": 13.20,
  "evidence": [
    {"type": "frame", "ref": "frames/000372.png", "observed": "标签晚于配音 cue 出现"},
    {"type": "audio_window", "ref": "audio/12.0-14.0.wav", "observed": "该窗口包含目标句"},
    {"type": "timeline", "ref": "timeline.json#cues[7]", "observed": "cue start_frame=372"}
  ],
  "issue": "画面标签滞后于对应句级 cue",
  "impact": "听到该概念时画面仍显示上一项",
  "repair": "把标签入场绑定到 cue 的 start_frame，并从源时间轴整片重渲染"
}
```

## 5. 状态、严重级和置信度

### 状态

- `pass`：检查项有足够证据且达到要求
- `warn`：存在可感知问题，但交付影响有限或需要用户取舍
- `fail`：证据充分且需要修复后再交付
- `missing_evidence`：审查所需证据缺失，结论保持开放

### 严重级

- `blocker`：核心内容错位、媒体损坏、音频缺失、字幕大面积缺失或播放状态未成立
- `major`：关键段落、核心枚举、主要字幕或音画同步存在明显缺陷
- `minor`：局部漂移、轻微遮挡、节拍瑕疵或术语不统一
- `note`：可选的风格和优化建议

### 置信度

- `high`：同一问题由多个证据类型相互印证
- `medium`：有画面或声音证据，但缺少对应冻结基准
- `low`：只有单次观察或主观判断，需补证据

## 6. 结论规则

- 任一 `blocker` 或未处理的 `major` 使总体状态至少为 `fail`。
- 只有 `minor`/`note` 时，总体状态可为 `warn`。
- 存在关键维度 `missing_evidence` 时，报告要写清楚“哪些结论尚未闭合”。
- 结论只描述当前媒体指纹对应的版本；新渲染必须生成新的 `run_id` 和报告。
