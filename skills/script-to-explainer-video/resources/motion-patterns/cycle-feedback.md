---
id: cycle-feedback
name: 循环与反馈
version: 1.0.0
---

# 循环与反馈

## 适用语义

用于观察—判断—执行—反馈、输入不断回流、状态持续迭代等闭环机制。

## 不适用

- 只有开始和结束的单向流程
- 单纯重复动画但不存在语义回流

## 对象模型

- stages
- directed_relations
- feedback_edge
- changing_state
- loop_condition

## 空间结构

- 闭环圆形路径
- 带回流箭头的线性路径
- 中心状态 + 外围循环阶段

圆形布局只有在所有阶段确实构成闭环时使用。

## 推荐状态链

```text
START_STATE
→ STAGES_REVEALED
→ FORWARD_FLOW
→ RESULT_STATE
→ FEEDBACK_EDGE
→ UPDATED_START
→ LOOP_HOLD
```

## 主要事件

- reveal
- connect
- flow
- update-state
- loop
- focus-condition

## 连续性

循环不应无限无变化重复。每轮至少改变一个状态、数值或判断，展示反馈产生的影响。

## 风险

- 回流箭头方向错误
- 线性流程被强行画成圆
- 循环条件没有说明
- 动画持续旋转但观众看不出状态变化
- 阶段过多导致标签拥挤

## 验收

- 观众能否指出反馈从哪里回到哪里
- 每一轮改变了什么
- 循环何时继续、何时停止
- 回流 cue 是否在口播说明反馈之后出现
