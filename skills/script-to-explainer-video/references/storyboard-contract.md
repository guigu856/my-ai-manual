# 分镜契约

`STORYBOARD.md` 是叙事和渲染之间的创作契约。它描述画面要完成的理解任务和状态变化，不承担最终帧号。

## Scene 与 Beat 的关系

- 一个 Scene 可以承载多个连续 Beat
- 一个 Beat 可以跨多个 Scene 展开
- Scene 的边界由视觉空间、关系结构或注意中心是否发生实质变化决定
- 不要把每句话机械做成一个独立 Scene

## Scene 必填字段

```yaml
scene_id: S02
beat_ids: [B02, B03]
visual_job: reframe
representation: diagram
semantic_topology: state-transformation
viewer_question: 问题到底出在哪里
start_state: 多个工具图标围绕人物，中心显示“不会用 AI”
end_state: 工具退居背景，任务描述框成为中心
preserve:
  - central_subject
exit:
  - excess_tool_icons
risks:
  - 信息过密
  - 转折提前泄露
```

## 状态链

每个 Scene 至少定义：

- `entry_state`：进入场景时观众看到什么
- `stable_states`：可以停留阅读的中间状态
- `transition_events`：状态如何变化
- `exit_state`：交给下一场景的画面状态

示例：

```yaml
states:
  - id: ST1
    meaning: 旧认知建立
    visible: [person, tool_cluster, old_claim]
  - id: ST2
    meaning: 旧认知产生负担
    visible: [person, overloaded_tool_cluster]
  - id: ST3
    meaning: 新解释出现
    visible: [person, task_box, new_claim]

events:
  - from: ST1
    to: ST2
    action: accumulate
  - from: ST2
    to: ST3
    action: replace-and-focus
```

State 必须是有语义的稳定画面，不是“动画进行到 30%”。

## 时间字段

分镜阶段只允许：

- Beat 引用
- Spoken Unit 引用
- cue 占位引用
- 相对顺序
- 预期节奏：fast / normal / deliberate / hold

禁止把估算秒数当最终时间。最终帧号由 `audio-meta.json` 和 `render-plan.json` 决定。

## 画面文字职责

每个 Scene 分开记录：

- `headline`：当前判断，尽量短
- `labels`：对象或关系名称
- `caption_ref`：对应字幕 cue
- `source_note`：数据或引用来源

标题、标签和字幕不得完整重复。

## 运动描述

分镜不写具体 CSS 或 TSX。使用 `references/motion-language.md` 中的语义动作：

- reveal
- connect
- accumulate
- separate
- compare
- transform
- replace
- collapse
- focus
- loop
- hold

若需要组合，写成 `replace-and-focus`，并明确先后顺序。

## 连续性字段

```yaml
continuity:
  incoming_anchor: center.subject
  preserve: [subject]
  transform:
    - tool_cluster -> background_context
  outgoing_anchor: center.task_box
```

每次跨 Scene 必须说明空间锚点和注意中心。直接全屏切换只在语义确实需要断裂时使用。

## 风险字段

至少检查：

- 画面是否与字幕重复
- 是否提前暴露下一 Beat 的结论
- 是否需要观众同时阅读多个长文本
- 连线、节点或标签是否可能互相遮挡
- 视觉隐喻是否可能误导
- 是否存在没有语义作用的运动

## Review Gate

分镜通过前逐 Scene 回答：

1. 这个 Scene 帮助观众理解了什么？
2. 为什么必须使用这个视觉形式？
3. 起态和终态分别表达什么？
4. 动画表达了哪种关系，而不只是“让元素动起来”？
5. 删除这个 Scene 后会损失什么？

无法回答的问题必须回到视觉策略重新设计。
