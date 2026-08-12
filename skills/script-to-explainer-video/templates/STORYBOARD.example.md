---
version: 1
aspect_ratio: 7:5
style_preset: minimal-editorial
caption_style: phrase-highlight
---

# Video Direction

- 主视觉语法：深色背景、少量高对比语义色、明确留白
- 主运动语法：建立、堆积、冻结、替换、聚焦
- 色彩语义：蓝色表示工具与操作；橙色表示任务定义；灰色表示未明确状态
- 连续对象：中心人物/主体轮廓贯穿前三个 Scene

# Scene S01：旧认知建立

```yaml
scene_id: S01
beat_ids: [B01, B02]
visual_job: orient
representation: object-metaphor
semantic_topology: accumulation-decay
viewer_question: 为什么大家一直找更多工具
start_state: 中心主体周围为空
end_state: 工具图标逐步堆满主体周围
headline: 不会用 AI，是工具太少？
labels: [模型, 插件, 工作流]
caption_ref: [B01, B02]
continuity:
  incoming_anchor: none
  preserve: [central_subject]
  outgoing_anchor: center.subject
risks:
  - 工具图标过多导致不可读
  - 标题与字幕重复
```

## States

```yaml
- id: S01_ST1
  meaning: 主体和问题建立
  visible: [central_subject, headline]
- id: S01_ST2
  meaning: 工具不断增加
  visible: [central_subject, tool_cluster]
- id: S01_ST3
  meaning: 工具数量成为主要注意中心
  visible: [central_subject, overloaded_tool_cluster]
```

## Events

```yaml
- from: S01_ST1
  to: S01_ST2
  action: accumulate
  cue_ref: B02.start
- from: S01_ST2
  to: S01_ST3
  action: focus
  cue_ref: B02.emphasis:一直换
```

# Scene S02：矛盾暴露

```yaml
scene_id: S02
beat_ids: [B03]
visual_job: compare
representation: diagram
semantic_topology: comparison
viewer_question: 工具增加后结果真的变好了吗
start_state: 延续工具堆积，右侧出现输出质量轨迹
end_state: 工具数量上升，输出质量仍不稳定
headline: 工具更多 ≠ 结果更稳
caption_ref: [B03]
continuity:
  incoming_anchor: center.subject
  preserve: [central_subject, tool_cluster]
  outgoing_anchor: center.subject
risks:
  - 两条趋势使用不同尺度造成误导
```

# Scene S03：认知重构

```yaml
scene_id: S03
beat_ids: [B04, B05]
visual_job: reframe
representation: diagram
semantic_topology: state-transformation
viewer_question: 真正影响输出的变量是什么
start_state: 工具集群仍占据主要空间
end_state: 工具退居背景，任务定义框成为中心，并展开目标、上下文、判断标准
headline: 真正变量：任务定义
labels: [目标, 上下文, 判断标准]
caption_ref: [B04, B05]
continuity:
  incoming_anchor: center.subject
  preserve: [central_subject]
  transform:
    - tool_cluster -> background_context
  outgoing_anchor: center.task_definition
risks:
  - 新结论提前出现
  - 三个标签与字幕同时堆叠
```

## States

```yaml
- id: S03_ST1
  meaning: 旧解释维持
  visible: [central_subject, tool_cluster]
- id: S03_ST2
  meaning: 旧解释冻结并失去权重
  visible: [central_subject, dimmed_tool_cluster]
- id: S03_ST3
  meaning: 任务定义成为新变量
  visible: [central_subject, task_definition]
- id: S03_ST4
  meaning: 任务定义由三个必要部分构成
  visible: [goal, context, success_criteria]
```

# Scene S04：结论收束

```yaml
scene_id: S04
beat_ids: [B06]
visual_job: emphasize
representation: kinetic-type
semantic_topology: state-transformation
viewer_question: 接下来应该练什么
start_state: 三个任务定义部分保持
end_state: 三个部分收束为“先定义任务”
headline: 先定义任务，再选择工具
caption_ref: [B06]
continuity:
  incoming_anchor: center.task_definition
  preserve: [task_definition]
  outgoing_anchor: center.final_claim
risks:
  - 大字结论停留时间不足
```
