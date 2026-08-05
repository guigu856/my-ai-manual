# Script to Explainer Video：架构说明

本文件面向维护者，解释 Skill 的职责边界。运行时 Agent 只需按 `SKILL.md` 的加载地图读取相关文件。

## 设计目标

- 让入口 Skill 保持短、稳定、可执行
- 把创作决策与渲染工程分层
- 让阶段产物可独立审核、版本化和失效
- 让 Remotion 与 HyperFrames 共用同一上游契约
- 让动效 Pattern 表达语义结构，而不是视觉皮肤

## 分层

### Orchestration

`SKILL.md` 只负责：触发范围、阶段顺序、Gate、失效规则、停止条件和交付报告。

### Creative References

`references/` 负责单一领域知识。每个文件只回答一类问题，避免重复全局规则。

### Motion Patterns

`resources/motion-patterns/` 负责语义拓扑到视觉状态链的映射，不包含 TTS、字幕、引擎命令和全局 QC。

### Machine Contracts

`schemas/` 描述可以被程序验证的数据。Markdown 产物负责人工可读创作决策，JSON 产物负责确定性执行。

### Examples

`templates/` 展示推荐格式，不应被当作固定内容模板。

## 阶段边界

```text
Intent / Brief
    ↓
Narrative / Script
    ↓
Visual Storyboard
    ↓  创作 Gate
Final Audio + Cues
    ↓
Render Plan
    ↓
Engine Adapter
    ↓
QC Evidence
```

创作 Gate 之前允许改写脚本和重做分镜。创作 Gate 之后音频成为执行主时钟；修改口播必须显式使下游失效。

## 为什么不使用超级单文件

意图、脚本、分镜、音频、渲染计划和 QC 的生命周期不同。单文件会导致：

- 自动推导字段与人工决策混合
- 上游修改后旧字段残留
- Agent 为追求“完整”一次性编造下游数据
- 审核无法绑定到准确版本

因此采用阶段文件 + hash 依赖。

## Markdown 与 JSON

使用 Markdown：

- BRIEF
- SCRIPT
- STORYBOARD
- QC 报告

使用 JSON：

- audio-meta
- captions
- render-plan
- probes

Markdown 负责解释和审阅；JSON 负责时间、事件和渲染。

## 新增 Reference

只有满足以下条件才新增：

- 属于独立知识领域
- 不应在主 Skill 每次加载
- 能被多个流程阶段复用
- 与现有文件不存在大面积重复

## 新增 Motion Pattern

Pattern 必须代表新的语义拓扑，至少能覆盖两个不同主题。单纯的新颜色、字体、卡片样式或转场效果不构成 Pattern。

## 新增引擎

新引擎只需实现 render-plan adapter。不得要求上游为特定引擎改变 Beat、Scene、State 和 Event 的语义。

## 版本

- 修改入口契约或阶段顺序：主版本升级
- 新增兼容 reference、pattern 或 schema 字段：次版本升级
- 修正文案和不影响契约的细节：补丁版本升级
