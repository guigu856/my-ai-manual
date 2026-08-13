---
name: ai-tip-short-video
description: |
  将日常使用 AI 的感悟、技巧或笔记，制作为 45–90 秒抖音竖屏技巧分享短视频。
  严格采用四段式结构（共鸣 → 问题本质 → 解决方案概要 → 反问互动），只讲重点，无私域引流口播。
  使用 Remotion 实现 kinetic typography 与统一系列动效；封面、标题与发布文案一并产出。
  完整提示词包与进阶资料不在视频内交付，由独立资料包 Skill 或人工进群流程处理。
  触发：用户提供 AI 使用笔记/碎碎念/主题，要求做技巧短视频、抖音 AI 干货、四段式短视频、Remotion 技巧视频等。
  不要用于：长文讲解、真人口播实拍剪辑、需要复杂连续 diagram 的长概念片、纯文案改写。
metadata:
  version: "1.0.0"
  engine: remotion
  aspect: "9:16"
---

# AI Tip Short Video（抖音 AI 技巧短视频）

将「日常 AI 使用笔记」转化为系列风格统一、高信息密度、可批量生产的竖屏短视频。
本 Skill 在仓库既有 `script-to-explainer-video` 之上做垂直特化：固定四段式叙事、强制 Remotion、9:16、page-isolated、无私域口播。

## 与 script-to-explainer-video 的关系

- **复用**：叙事纪律、动效语言、视觉任务、质量门禁、render-plan 思想、Remotion 实现约束。
- **特化**：固定四段式；默认 9:16；默认 45–90s；默认 kinetic-type 为主；发布物料（封面/标题/描述）纳入交付；视频脚本文案禁止任何进群/私域引导。
- **执行时**：通用细则优先读取 `../script-to-explainer-video/references/`；本 Skill 的 `references/` 只写冲突时的覆盖规则与系列设计系统。

## 核心原则（不可违反）

1. **四段式唯一结构**  
   共鸣（8–12s）→ 问题本质（12–18s）→ 解决方案概要（20–30s）→ 反问互动（5–8s）。  
   总时长目标 45–90 秒。禁止额外「总结升华」「产品软广」「资料包口播」。

2. **视频内零私域**  
   口播与画面文字不得出现「关注进群」「领资料包」「私信领取」等引导。  
   私域转化只允许出现在发布附加文案与评论区自评。

3. **只讲重点**  
   解决方案阶段最多给出 1–3 个可执行方法概要。完整提示词模板、多场景变体留给资料包。

4. **动效服务于理解，不为动而动**  
   遵守 `script-to-explainer-video/references/motion-language.md` 与 `visual-design-principles.md`。  
   每个 Scene 只有一个主要视觉焦点；默认 page-isolated。

5. **Remotion 帧驱动**  
   所有动画必须由 `useCurrentFrame()` + `interpolate()`（优先）或 `spring()` 驱动。  
   禁止 CSS transitions / animations、Tailwind animate 类、`Date.now()`、随机数。  
   参考官方与社区约束：始终 clamp；`useCurrentFrame` 相对最近 `<Sequence>`；元素入场必须有动画，禁止硬切静止出现。

6. **系列视觉锁定**  
   全系列共享同一 `style_lock`（主色、字体、标题层级、转场时长、Logo 位置、安全区）。  
   封面与视频片头使用同一标题公式，保证「一眼知道讲什么问题」。

7. **确定性与可检查**  
   输出可复现源码 + render-plan 思想的时间轴 + 最终 MP4 + 发布物料。

## 输入

至少其一：

- 原始笔记 / 碎碎念 / 使用感悟
- 明确主题（如「如何解决 AI 脑补误判」）
- 已写好的四段式草稿

可选：系列名、主色、已有 Logo、目标时长、声线偏好。

信息不足时采用默认值继续；仅当核心痛点无法识别时暂停确认。

## 输出作品包契约

```text
<project>/
├── BRIEF.md                 # 核心痛点、受众、一句话价值
├── SCRIPT.md                # 四段式口播（无私域）
├── STORYBOARD.md            # 分镜 + 状态链
├── PUBLISH.md               # 标题、封面文案、发布描述、建议置顶评论（含进群引导）
├── cover/                   # 封面图或生成提示
├── audio/                   # 可选：master + cues
├── src/                     # Remotion 源码
│   ├── Root.tsx
│   ├── Video.tsx
│   ├── theme/
│   ├── scenes/
│   └── components/
├── render-notes.md          # 时长、fps、composition id、渲染命令
└── final.mp4                # 成片（可后置）
```

## 工作流

### 阶段 0：识别新建或续作

已有项目则从最后通过的 Gate 继续；上游变更按失效规则清理下游。不覆盖用户手改文件。

### 阶段 1：BRIEF（Gate 1）

产出 `BRIEF.md`：

- 核心痛点（一句话）
- 目标受众（日常用 AI 的创作者/职场人等）
- 看完后应掌握的方法概要
- 系列归属与视觉方向（默认 kinetic 知识卡）

**Gate 1**：能用「如何解决 X」或等价标题公式概括，且只保留一个主命题。

### 阶段 2：SCRIPT 四段式（Gate 2）

严格按下列时间预算写口播：

| 段 | 角色 | 时长 | 要求 |
|----|------|------|------|
| 1 共鸣 | 点出痛点，制造认同 | 8–12s | 口语化问题场景，禁止解决方案抢跑 |
| 2 本质 | 揭示原因 | 12–18s | 简洁机制，建立专业感，不堆术语 |
| 3 方案 | 1–3 个可执行方法概要 | 20–30s | 编号清晰；只给骨架，不给完整长提示词 |
| 4 反问 | 互动收束 | 5–8s | 只反问使用经验；禁止进群话术 |

产出 `SCRIPT.md`。  
**Gate 2**：无私域语句；每段推进主命题；删任意段会损伤完整性。

### 阶段 3：STORYBOARD + 发布物料（Gate 3）

读取本 Skill `references/series-design-system.md`、`references/remotion-constraints.md`，  
并复用 `../script-to-explainer-video/references/visual-design-principles.md`、`motion-language.md`。

默认生产剖面：`page-isolated`。  
表达形式优先：`kinetic-type`（大标题、关键词、编号卡片）。  
每段对应 1–3 个 Scene；每个 Scene 写清 visual_job、起态、状态链、终态、hold。

同时产出 `PUBLISH.md`：

- 标题（「如何解决 + 问题」或「AI + 场景 + 方法」）
- 封面文案与视觉描述（大号标题 + 关键词高亮 + 系列标识）
- 发布描述（可含进群引导）
- 建议评论区自评（可含进群引导）

**Gate 3**：分镜覆盖四段；画面不是字幕复述；封面 1 秒内可读懂主题；视频脚本仍无私域。

### 阶段 4：音频（可选但推荐）

若需要口播：生成配音并取得 cue，作为主时钟。  
若纯画面字卡视频：可按分镜估算帧数，但仍须固定 fps 与总帧数。

### 阶段 5：Remotion 实现（Gate 5）

遵守 `references/remotion-constraints.md`（来自官方 remotion-best-practices、社区 video-director、本仓库 explainer 约束的提炼）：

- 手动搭建项目结构，禁止依赖交互式 `create-video` wizard
- 时间全部来自 frame / Sequence；`interpolate` 必须 clamp
- 主题 token 集中在 `theme/`
- 每个元素入场有动画；场景间默认短 cross-dissolve 或统一硬切+入场（系列内选一种并锁定）
- 文字安全区：避开底部 15% 与边缘；竖屏关键字号足够大
- 先渲染关键 still，再渲染完整视频

**Gate 5**：源码可渲染；无 CSS 动画；无绝对秒数散落在组件内。

### 阶段 6：质量验收（Gate 6）

检查清单（精简版，完整语义见 explainer quality-gates）：

- 四段时长与节奏是否符合预算
- 视频内是否出现任何私域引导
- 标题/封面是否一眼说明问题
- 文字是否可读、无重叠、无出安全区
- 动效是否服务焦点（非装饰漂浮）
- 系列 style_lock 是否一致

通过后交付作品包。

## 默认参数

| 参数 | 默认值 |
|------|--------|
| 画幅 | 9:16（1080×1920） |
| fps | 30 |
| 时长 | 45–90s |
| 引擎 | Remotion |
| 生产剖面 | page-isolated |
| 主表达 | kinetic-type + 编号卡片 |
| BGM | 默认无；若有则极轻且不压人声 |
| 字幕 | 可开；与口播语义短语对齐；不与画面大字重复整句 |
| 私域 | 仅 PUBLISH.md |

## 失效规则

- BRIEF 变更主痛点 → 下游全部失效
- SCRIPT 变更口播 → STORYBOARD、音频、实现、成片失效
- STORYBOARD 仅改布局 → 音频可复用，实现与成片失效
- style_lock 变更 → 实现与成片失效

## 停止条件

- 无法识别单一核心痛点
- 用户坚持在视频口播中加入进群引导（应拒绝并改到 PUBLISH）
- Remotion 依赖缺失且无法安装
- 事实性错误会影响方案可信度

## Reference 地图

| 主题 | 文件 |
|------|------|
| 系列视觉与封面 | `references/series-design-system.md` |
| Remotion 硬约束 | `references/remotion-constraints.md` |
| 四段式话术 | `references/four-act-script.md` |
| 通用动效/视觉 | `../script-to-explainer-video/references/motion-language.md` 等 |
| 成片审查 | `../explainer-video-review/SKILL.md` |
