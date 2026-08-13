---
name: ai-tip-short-video
description: |
  将日常使用 AI 的感悟、技巧或笔记，制作为 45–90 秒技巧分享短视频。
  严格四段式：共鸣 → 问题本质 → 解决方案概要 → 反问互动。只讲重点；视频内禁止私域引流。
  画面与动效必须按四段镜头配方表选型，禁止自由发挥。默认 Remotion、7:5、kinetic typography。
  封面、标题与发布文案一并产出；完整提示词包不在视频内交付。
  触发：AI 使用笔记/碎碎念/主题、技巧短视频、抖音 AI 干货、四段式短视频、Remotion 技巧视频。
  不要用于：长文讲解、真人口播实拍剪辑、复杂连续 diagram 长片、纯文案改写。
metadata:
  version: "1.1.1"
  engine: remotion
  aspect: "7:5"
---

# AI Tip Short Video（AI 技巧短视频）

将「日常 AI 使用笔记」转化为系列风格统一、高信息密度的短视频。
本 Skill **自包含**：不依赖仓库内其他 Skill；仅凭本目录即可完成从文案到 Remotion 实现的约束。

## 核心原则（不可违反）

1. **四段式唯一结构**  
   共鸣（8–12s）→ 问题本质（12–18s）→ 解决方案概要（20–30s）→ 反问互动（5–8s）。  
   总时长 45–90 秒。禁止额外总结升华、产品软广、资料包口播。

2. **视频内零私域**  
   口播与画面不得出现关注进群、领资料包、私信领取等。  
   私域仅允许写在 `PUBLISH.md`（发布描述与建议评论）。

3. **动效按配方表路由，禁止自由发挥**  
   必须读取并遵守 `references/four-act-motion-playbook.md`。  
   每段只能使用该段「允许配方」；文案角色决定配方，不得先想酷炫再找理由。

4. **只讲重点**  
   方案段最多 1–3 条可执行方法骨架；完整提示词留给资料包渠道。

5. **Remotion 帧驱动**  
   遵守 `references/remotion-implementation.md`：仅 `useCurrentFrame` + `interpolate`/`spring`；禁止 CSS/Tailwind 动画；必须 clamp；入场必动、结论必 hold。

6. **系列视觉锁定**  
   遵守 `references/series-design-system.md`。全系列共享 style_lock；封面与片头同一标题公式。

7. **确定性交付**  
   可复现源码 + 成片说明 + 发布物料。

## 输入

至少其一：原始笔记/碎碎念、明确主题、已写四段草稿。  
可选：系列名、主色、Logo、时长、声线、画幅覆盖（未指定时默认 7:5）。  
信息不足用默认值；仅当核心痛点无法识别时暂停确认。

## 输出作品包

```text
<project>/
├── BRIEF.md
├── SCRIPT.md              # 四段口播，无私域
├── STORYBOARD.md          # 每段标注选用的配方 ID（如 A1、C1）
├── PUBLISH.md             # 标题、封面、描述、建议评论（私域仅此处）
├── cover/
├── audio/                 # 可选
├── src/                   # Remotion
│   ├── Root.tsx
│   ├── Video.tsx
│   ├── theme/
│   ├── scenes/
│   └── components/
├── render-notes.md
└── final.mp4              # 可后置
```

## 工作流

### 阶段 0：新建或续作

已有项目从最后通过 Gate 继续。不覆盖用户手改文件。

### 阶段 1：BRIEF（Gate 1）

- 核心痛点（一句话）
- 受众
- 看完应掌握的方法概要
- 系列与视觉方向（默认 kinetic 知识卡）
- 画幅（默认 7:5 / 1400×1000；仅当用户明确要求时覆盖）

**Gate 1**：能用「如何解决 X」概括，且单一主命题。

### 阶段 2：SCRIPT（Gate 2）

读取 `references/four-act-script.md`。

| 段 | 时长 | 要求 |
|----|------|------|
| 共鸣 | 8–12s | 场景化痛点；方案不抢跑 |
| 本质 | 12–18s | 机制一句话，少术语 |
| 方案 | 20–30s | 1–3 条骨架；条数将锁定画面 |
| 反问 | 5–8s | 只问经验；禁止进群话术 |

**Gate 2**：无私域；每段推进主命题。

### 阶段 3：STORYBOARD + 发布（Gate 3）

**必读** `references/four-act-motion-playbook.md` 与 `references/series-design-system.md`。

对每一段：

1. 根据文案职责判定角色（共鸣/本质/方案/反问）
2. 仅从该段允许配方中选择（写入 STORYBOARD，如 `recipe: C1`）
3. 写清主焦点、入场、hold、退场；方案段条数与口播一致且顺序一致

同时写 `PUBLISH.md`（标题、封面描述、发布文案、建议置顶评论）。

**Gate 3**：每段有合法配方 ID；画面非字幕复读；封面一眼可读主题；视频脚本仍无私域。

### 阶段 4：音频（推荐）

有口播则生成配音与 cue 作主时钟；纯字卡则固定 fps 与总帧数。

### 阶段 5：Remotion 实现（Gate 5）

必读 `references/remotion-implementation.md`。  
Composition 默认 `width: 1400, height: 1000`（7:5）。  
组件只实现 playbook 中已选配方；不得引入未列出的运动类型。

**Gate 5**：可渲染；无 CSS 动画；无散落绝对秒数；配方与分镜一致。

### 阶段 6：验收（Gate 6）

- 四段时长与节奏
- 视频内零私域
- 每段配方合法且焦点单一
- 方案条数/顺序与口播一致
- 安全区与可读性
- style_lock 与画幅一致

## 默认参数

| 参数 | 默认 |
|------|------|
| 画幅 | **7:5（1400×1000）**；仅用户明确要求其他比例时覆盖 |
| fps | 30 |
| 时长 | 45–90s |
| 引擎 | Remotion |
| 背景 | 单集内深或浅二选一锁死 |
| 段间转场 | 硬切 + 新段入场（系列可改为统一短 dissolve 8–12 帧，但全系列只能选一种） |
| BGM | 默认无 |
| 私域 | 仅 PUBLISH.md |

## 失效规则

- BRIEF 变更主痛点 → 下游全失效
- SCRIPT 变更 → 分镜/实现/成片失效
- 配方或 style_lock 或画幅变更 → 实现与成片失效

## 停止条件

- 无法识别单一痛点
- 用户要求视频内出现进群引导（拒绝，改到 PUBLISH）
- 试图使用 playbook 未列出的动效类型且无改文案角色
- Remotion 依赖缺失无法安装

## Reference 地图

| 文件 | 用途 |
|------|------|
| `references/four-act-motion-playbook.md` | **四段镜头配方强制路由** |
| `references/remotion-implementation.md` | Remotion 实现硬约束 |
| `references/series-design-system.md` | 封面、标题、style_lock、画幅 |
| `references/four-act-script.md` | 口播四段与零私域 |
