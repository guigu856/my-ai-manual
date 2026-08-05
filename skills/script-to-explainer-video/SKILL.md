---
name: script-to-explainer-video
description: 把观点、想法、讲解稿或口播脚本转成经过叙事设计、视觉分镜、配音对齐、程序化动效渲染和质量验收的概念讲解视频。适用于无真人出镜的观点视频、知识讲解、技术解释、概念动画，以及需要 Remotion 或 HyperFrames 实现的短视频。用户只要求改文案、只做字幕或只剪已有真人口播时不要使用。
version: 2.0.0
---

# Script to Explainer Video

把文本变成可观看的概念动效讲解视频。这个 Skill 负责整条生产线的编排，不在入口文件中重复所有叙事、设计、音频、动画和引擎细则；执行到对应阶段时再读取相关 reference。

## 核心原则

1. **先确定要让观众理解什么，再决定画面怎么动。** 动画服务于注意力、逻辑、节奏和情绪，不以“丰富画面”为目标。
2. **先锁定叙事与视觉分镜，再生成最终配音。** 允许前期使用估算时长；分镜确认后生成最终音频。
3. **最终音频是执行阶段唯一主时钟。** 字幕、场景、状态和动画事件都引用实测 cue，不凭感觉写死绝对秒数。
4. **语义层级不可混用。** Section、Beat、Spoken Unit、Caption Cue、Scene、State、Event 各自独立，不强制一一对应。
5. **每个画面必须有明确视觉任务。** 画面应承担建立对象、具体化、解释、对比、证明、强调、重构认知、过渡或留白之一。
6. **先设计状态链，再实现动画。** 每个场景必须有稳定起态、变化过程和终态；实现只负责忠实执行分镜。
7. **确定性渲染，可检查交付。** 禁止依赖实时计时器、随机数或不可复现状态；必须输出检查材料和最终成片。

## 输入

至少提供以下之一：

- 完整口播脚本
- 观点或想法草稿
- 需要讲解的主题、文章、笔记或资料
- 已存在的 `BRIEF.md`、`SCRIPT.md` 或 `STORYBOARD.md`

可选信息：平台、画幅、时长、受众、风格、声线、品牌规范、必须保留的原文、已有素材。

信息不足但不影响主线时按默认值继续，不为了次要参数反复询问。只有核心观点、目标受众或是否允许改写存在实质歧义时才需要确认。

## 输出目录契约

每个项目使用独立目录：

```text
<project>/
├── BRIEF.md
├── SCRIPT.md
├── STORYBOARD.md
├── audio/
│   ├── master.wav
│   ├── audio-meta.json
│   └── captions.json
├── render-plan.json
├── src/ 或 compositions/
├── qc/
│   ├── qc-report.md
│   ├── contact-sheet.png
│   └── probes.json
└── final.mp4
```

阶段产物分开保存。不要再使用一个不断变异的超级 `script-package.json` 同时承载意图、分镜、音频、渲染和 QC。

## 工作流

### 阶段 0：识别新建或续作

- 已有项目时，读取现有阶段文件并从最后一个通过 Gate 的阶段继续。
- 上游文件发生变化时，按“失效规则”清理或重建下游产物。
- 不覆盖用户手工修改的文件；先保留副本或在报告中说明差异。

### 阶段 1：确定创作目标

读取：

- `references/narrative-design.md`
- `templates/BRIEF.example.md`

产出 `BRIEF.md`，至少确定：

- 核心观点
- 目标受众
- 观众当前认知
- 希望形成的新认知
- 表达态度与情绪
- 视频类型与平台
- 是否保留原文
- 目标时长与画幅

**Gate 1：** 能用一句话说清“观众看完后应理解什么”，且视频只保留一个主命题。

### 阶段 2：叙事拆解与口播定稿

读取：

- `references/script-decomposition.md`
- `templates/SCRIPT.example.md`

产出 `SCRIPT.md`。按语义命题拆 Beat，不按标点机械切句。每个 Beat 标注：

- narrative role
- 与前文关系
- viewer takeaway
- emphasis
- 可否删减

允许一个 Scene 覆盖多个 Beat，也允许一个 Beat 被多个 Spoken Unit 或 Caption Cue 承载。

**Gate 2：** 每个 Beat 都推进主命题；删除任何 Beat 后若不影响理解，应直接删除。

### 阶段 3：视觉策略与分镜

读取：

- `references/visual-design-principles.md`
- `references/storyboard-contract.md`
- `resources/motion-patterns/index.md`
- `templates/STORYBOARD.example.md`

先为每个 Beat 指定 `visual_job`，再选择 representation、semantic topology 和 motion behavior。不要从“这里该用什么转场”开始设计。

产出 `STORYBOARD.md`，每个 Scene 至少包含：

- 承载哪些 Beat
- 视觉任务
- 表达形式
- 起始构图
- 关键状态链
- 终态
- 与前后场景的连续关系
- 需要保留或退出的元素
- 风险点

此阶段只使用相对节拍或 cue 引用，不写最终绝对秒数。

**Gate 3：** 分镜已覆盖全部 Beat；画面不是字幕复述；每个 Scene 都能说明它帮助观众理解了什么。最终脚本与分镜在此阶段锁定。

### 阶段 4：生成最终配音和时间信息

读取：

- `references/audio-and-timing.md`
- `references/caption-system.md`
- `schemas/audio-meta.schema.json`

根据已锁定的 `SCRIPT.md` 生成最终配音。输出：

- `audio/master.wav`
- `audio/audio-meta.json`
- `audio/captions.json`

必须取得句级 cue；能够取得词级 cue 时一并保留。响度、静音、削波、采样率和实际总时长通过后，音频才成为唯一主时钟。

**Gate 4：** 音频可正常播放，cue 覆盖全部 Spoken Unit，音频 hash 已记录。

### 阶段 5：编译渲染计划

读取：

- `references/motion-language.md`
- `references/engine-routing.md`
- `schemas/render-plan.schema.json`

把 `STORYBOARD.md` 的状态链映射到真实音频 cue，生成 `render-plan.json`。

事件应引用 cue：

```json
{
  "event": "reframe_reveal",
  "cue_ref": "B03.word:真正",
  "offset_frames": -2
}
```

禁止把 storyboard 中的估算时长直接当成最终帧号。渲染计划至少包含：画布、fps、Scene 区间、State 区间、Event、字幕引用、资源引用和引擎适配信息。

**Gate 5：** 所有 Scene、State 和 Event 都能追溯到 Beat 与音频 cue；不存在孤立动画。

### 阶段 6：实现与渲染

根据 `references/engine-routing.md` 选择 Remotion 或 HyperFrames。

实现要求：

- 帧驱动、可复现
- 从 `render-plan.json` 读取时间，不在组件内部散落绝对秒数
- 布局和连接点由统一坐标与约束计算
- 颜色、字体、间距和 motion token 全片一致
- 先渲染关键状态 still，再渲染完整视频

发现分镜问题时回到阶段 3；发现 timing 问题时回到阶段 4 或 5。不要用临时代码掩盖上游错误。

### 阶段 7：质量验收

读取：

- `references/quality-gates.md`
- `references/caption-system.md`

按四层检查：

1. 叙事：画面是否服务当前观点
2. 时序：语音、字幕、状态和动画是否同步
3. 空间：越界、遮挡、漂移、连线、层级和安全区
4. 技术：帧率、编码、音频、时长、缺失资源和容器

检查采用三级策略：

- 程序检查全部帧和媒体参数
- 每个 Scene 检查入场、稳定态、变化中点和退场
- 复杂转场、重组、连线和遮挡区间做密集逐帧检查

输出 `qc/qc-report.md`、接触表、探测数据和 `final.mp4`。

**Gate 7：** 所有阻断项清零后才交付。

## 默认判断

| 参数 | 默认值 |
|---|---|
| 画幅 | 明确短视频平台时 9:16；B站/YouTube/官网时 16:9；完全未知时 16:9 |
| 帧率 | 30fps；高密度运动或特殊要求再提高 |
| 时长 | 由内容决定，不为了凑时长填充画面 |
| 风格 | 先从题材、受众和态度判断，不默认所有技术内容都使用深色科技风 |
| BGM | 默认不添加；需要时确保版权并以不压人声为准 |
| 字幕 | 默认开启，按语义短语切分，不机械逐字堆叠 |
| 引擎 | React 组件和数据驱动复杂度高时优先 Remotion；HTML/GSAP/多运行时动效时优先 HyperFrames |

## 文件失效规则

- `BRIEF.md` 改变核心观点或受众：使 `SCRIPT.md` 及全部下游失效。
- `SCRIPT.md` 改变口播内容：使 `STORYBOARD.md`、audio、render plan 和渲染结果失效。
- `STORYBOARD.md` 只改布局但不改口播：audio 可复用，render plan 与渲染结果失效。
- `master.wav` 或 cue 改变：render plan、字幕渲染和成片失效。
- 仅改视觉样式 token：分镜和音频可复用，重新实现与渲染。

每个阶段记录上游文件 hash。不得在上游改变后继续使用旧的审核或旧时间轴。

## 停止条件

遇到以下情况停止并明确报告：

- 核心观点无法从输入中确定
- 脚本存在未经核实且会影响结论的事实主张
- 最终音频无法获得可靠 cue
- 引擎或媒体依赖缺失，且没有等价替代方案
- 版权或授权不明确的素材是成片必要组成
- QC 出现未解决的阻断问题

## 交付报告

最终报告必须包含：

- 核心观点与目标受众
- 使用的叙事结构和视觉策略
- 最终时长、画幅、fps 和引擎
- 输出文件路径
- QC 结果
- 已知限制或需要人工复核的部分

## Reference 加载地图

| 阶段 | 必读文件 |
|---|---|
| 创作目标 | `references/narrative-design.md` |
| 叙事拆解 | `references/script-decomposition.md` |
| 视觉分镜 | `references/visual-design-principles.md`、`references/storyboard-contract.md` |
| 动效类型 | `resources/motion-patterns/index.md` 及匹配的 pattern |
| 配音时间轴 | `references/audio-and-timing.md` |
| 字幕 | `references/caption-system.md` |
| 动画实现 | `references/motion-language.md` |
| 引擎选择 | `references/engine-routing.md` |
| 验收 | `references/quality-gates.md` |
