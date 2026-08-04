---
name: script-to-explainer-video
description: |
  Use this Agent Skill when a user provides a workflow, script, prompt, oral script, or concept brief and asks to turn it into a narrated concept-motion explainer video. It covers script freezing, measured voiceover, a canonical timeline, Remotion or HyperFrames motion, captions, rendering, and production handoff. Trigger on requests such as “把这段口播做成概念动效视频” or “用配音驱动字幕和画面”。Exclude script-only rewriting, caption-only work, existing-footage editing, reference-video analysis, and post-render quality audits; route the last case to `explainer-video-review`.
metadata:
  author: guigu856
  version: "1.3.0"
---

# 脚本 → 概念动效视频生产 Skill

## 职责边界

本 Skill 负责：

- 将口播脚本或观点文案冻结为可执行分段
- 合成并验收配音，采集句级 cue
- 生成以音频为主时钟的 `timeline.json`
- 选择动效资源，完成场景设计与 Remotion / HyperFrames 实现
- 生成字幕、渲染成片并完成生产前置检查
- 将成片和证据交接给 `../explainer-video-review/SKILL.md`

本 Skill 不负责：

- 只改写文章、标题或口播文案
- 只给已有视频加字幕
- 编辑已有实拍素材、参考视频学习或镜头拆解
- 对最终 MP4 做独立的视觉质量审查

成片审查发现问题后，回到源文件或时间轴修复，整片重新渲染，再交给审查 Skill 复检。

## 输入与输出

输入：

- 口播脚本、观点文案、产品说明或概念 brief
- 用户指定的平台、比例、帧率、声线、视觉风格和交付格式
- 已有 Remotion / HyperFrames 工程及其资源（若存在）

输出：

- 冻结后的 `segments.json`
- 最终配音和句级 cue
- `timeline.json`
- 场景设计与动效实现
- 字幕文件（SRT/VTT 或工程内字幕数据）
- 可播放 MP4、渲染工程和生产交接信息

## 三条生产契约

1. **音频是主时钟**：所有场景、动效、字幕和转场时机从实测音频 cue 推导。
2. **时间轴只有一个来源**：Remotion、HyperFrames、字幕和检查流程都读取同一份 `timeline.json`。
3. **交付必须有复检证据**：生产检查与成片审查是两个阶段；源文件修复后必须整片复渲。

## Router Rules

- Trigger when the request turns a script, workflow, prompt, oral script, or concept brief into a narrated concept-motion explainer video.
- Require a production artifact, not script-only rewriting, caption-only work, existing-footage editing, reference-video analysis, or post-render auditing.
- Route post-render visual, subtitle, spatial-continuity, or audio-sync review to `../explainer-video-review/SKILL.md`.

## Compact Workflow

1. Freeze intent, script segments, platform, aspect ratio, and delivery format.
2. Produce and measure voiceover; record sentence-level cues.
3. Generate and validate `segments.json`, `timeline.json`, and subtitle data.
4. Route semantic concepts to motion resources and implement scenes in Remotion or HyperFrames.
5. Render representative frames, run production preflight, render the complete MP4, and hand off evidence.

## Gate Ladder

- **Input gate**: intent, script, platform, and output format are known; unresolved conflicts are recorded.
- **Audio gate**: voiceover is listenable and measured; cue boundaries are recorded.
- **Timeline gate**: one canonical timeline passes structural validation.
- **Render gate**: representative frames and the complete MP4 are rendered from that timeline.
- **Review gate**: the companion review Skill receives the MP4, frozen sources, timeline, captions, and evidence bundle.

## Output Contract

- Return frozen `segments.json`, measured voiceover and cues, canonical `timeline.json`, captions, scene implementation, rendered MP4, and handoff evidence.
- Mark provider-render, playback, and human-review results as `missing evidence` until they are actually observed.
- When a review finds a source or cue defect, repair the source, rerender the whole video, and submit a new evidence bundle.

## 执行流程

### 1. 冻结意图和文稿

确认核心观点、目标受众、平台、输出格式和视觉边界。按语义切分，每段表达一个完整观点，写入 `segments.json`。`title` 只保留短点题词或模块名，默认不超过 8 个汉字。

用户未指定参数时，使用本 Skill 的默认值；只有缺少脚本、无法确定输入文件或渲染工程状态互相矛盾时才提出阻塞问题。

### 2. 合成并验收配音

逐段合成配音，收集句级起止时间，统一音频格式并完成响度、削波、异常静音和总时长检查。试听通过后才建立画面时间轴。

### 3. 建立主时间轴

按 [音频—时间轴契约](references/audio-timeline-contract.md) 生成 `timeline.json`。帧区间使用半开区间 `[start_frame, end_frame)`；所有 cue 必须落在所属段落内并保持顺序。

### 4. 选择动效资源并设计场景

先判断脚本的语义拓扑，再读取 [动效资源索引](resources/motion-patterns/index.md)。有匹配资源时按资源契约执行；没有匹配资源时记录资源状态并做局部场景设计，不把临时方案伪装成已归档资源。场景先写状态链、布局、安全区、锚点和转场，再编码。

### 5. 实现、渲染和生产检查

动效、字幕和转场从 `timeline.json` 读取。先渲染代表帧检查构图与文字，再完成整片渲染和音频合成。按 [字幕、质量与交接](references/subtitle-qc-and-handoff.md) 完成结构检查和交接准备。

### 6. 交接与修复循环

把 MP4、冻结文稿、音频、时间轴、字幕和检查结果交给 `explainer-video-review`。审查结果若包含问题，修复源文件或 cue 数据，整片重新渲染并再次交接；旧的成片证据不沿用到新版本。

## 默认参数

| 参数 | 默认值 | 覆盖条件 |
|---|---|---|
| 比例 | 未说明时 16:9 | 平台或用户指定竖屏时使用 9:16 |
| 帧率 | 30fps | 已有工程或用户指定时跟随工程 |
| 风格 | 技术观点默认深色极简、底色加双语义色 | 用户指定风格优先 |
| 分段 | 每段一个完整观点，通常 1–3 句 | 由脚本密度和实际配音调整 |
| 节拍 | 句级 cue | 所有时间相关动作均以实测 cue 为准 |
| BGM | 用户明确要求后再加入 | 先确认来源和混音目标 |

## 资源与验证

- 生产规则：[意图与输入输出契约](references/intent-and-contract.md)
- 时间轴：[音频—时间轴契约](references/audio-timeline-contract.md)
- 视觉实现：[视觉与动效规则](references/visual-motion-rules.md)
- 字幕与交接：[字幕、质量与交接](references/subtitle-qc-and-handoff.md)
- 时间轴校验：`python scripts/validate_timeline.py --project <project-dir>`
- 触发回归：`python scripts/trigger_eval.py . --cases evals/trigger_cases.json`

## 完成条件

- `segments.json` 已冻结，字幕和画面没有脱离冻结稿
- 配音通过信号级检查，句级 cue 已记录
- `timeline.json` 通过结构校验，渲染时没有另造时间轴
- 代表帧和整片均已渲染，音频、视频、字幕时长一致
- 交接材料完整，审查 Skill 的结果已处理或明确标记为待处理
