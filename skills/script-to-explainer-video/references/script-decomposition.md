# 脚本拆解规范

脚本拆解的目标不是把文本切碎，而是建立“观点如何被理解”的结构。

## 七个层级

### Section

一个完整叙事章节，例如“旧认知”“矛盾暴露”“新解释”。Section 管理较大的认知阶段，不直接等于镜头。

### Beat

观众需要理解的一个语义命题。Beat 是创作与追踪的核心单位。

### Spoken Unit

一次自然说出的口语单位。一个 Beat 可以拆成多个 Spoken Unit；多个短 Beat 也可以合并为一个 Spoken Unit。

### Caption Cue

一次字幕显示单位。按可读性和语义短语切分，不等于 Spoken Unit。

### Scene

保持同一视觉空间和主要关系的连续场景。Scene 可以覆盖多个 Beat。

### State

Scene 中一个可稳定阅读的视觉状态，例如“旧认知完整展示”“对比关系建立”。

### Event

State 之间的变化，例如出现、连接、替换、聚焦、坍缩或重组。

## Beat 拆分标准

在以下位置考虑新 Beat：

- 提出新的判断
- 因果关系发生推进
- 叙事角色改变
- 从抽象进入例子
- 从例子返回结论
- 出现转折、限制或反例
- 观众需要形成新的中间理解

不要因为逗号、句号或字数达到某个阈值就机械拆分。

## Beat 字段

每个 Beat 至少包含：

```yaml
id: B03
section: SEC02
narration: 真正的问题，往往不是工具掌握得不够多
narrative_role: reframe
relation_to_previous: contradiction
viewer_takeaway: 问题不在工具数量
emphasis:
  - 真正的问题
optional: false
source_span: 原稿对应文本
```

推荐的 `relation_to_previous`：

- `continue`
- `cause`
- `result`
- `contrast`
- `contradiction`
- `example`
- `evidence`
- `zoom-in`
- `zoom-out`
- `condition`
- `exception`
- `summary`

## 信息密度检查

一个 Beat 同时包含多个动作、对象和结论时，应拆分。判断方法：

- 是否需要两个不同画面才能解释？
- 是否包含“但是、因此、同时、除非”等不同关系？
- 观众是否必须先理解前半句才能理解后半句？

若答案为是，通常需要拆分。

## 冗余检查

对每个 Beat 问：

1. 它是否推进主命题？
2. 它是否只是换一种说法重复上一 Beat？
3. 它是否提供必要例子或证据？
4. 删除后观众是否仍能完整理解？

可删除但不影响理解的 Beat 应删除，而不是缩成更快的动画。

## 口语化处理

- 一句只承载一个主要判断
- 明确代词指向
- 避免书面长定语
- 技术名词首次出现时建立最小解释
- 把括号信息改成自然插入语或删除
- 给转折和结论留出可感知停顿

## SCRIPT.md 结构

```markdown
---
version: 1
core_claim: 任务表达比工具数量更重要
estimated_duration: 45s
rewrite_mode: allowed
---

# Section 1：旧认知

## B01
- role: orient
- relation: start
- takeaway: 很多人把不会用 AI 归因于工具少
- narration: 很多人觉得自己不会用 AI，是因为掌握的工具还不够多。
- emphasis: 工具还不够多

## B02
...
```

## 时间估算

在最终配音前只做规划估算：

- 中文普通讲解可暂按每秒 4～5 个汉字估算
- 复杂技术句和强调句应降低速度
- 估算只用于判断整体篇幅和分镜可行性
- 估算不得直接写入最终渲染帧号

## Gate 检查

- 全文 Beat 覆盖原稿核心语义
- 每个 Beat 有明确 narrative role 和 takeaway
- Beat 之间关系可追踪
- 没有仅为“画面丰富”保留的无效句子
- 主命题没有在多个结论之间摇摆
