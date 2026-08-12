# Script to Explainer Video：架构说明

本文件面向维护者，解释 Skill 的职责边界。运行时 Agent 只需按 `SKILL.md` 的加载地图读取相关文件。

## 设计目标

- 让入口 Skill 保持短、稳定、可执行
- 把创作决策与渲染工程分层
- 让阶段产物可独立审核、版本化和失效
- 让 Remotion 与 HyperFrames 共用同一上游契约
- 让动效 Pattern 表达语义结构，而不是视觉皮肤
- 默认控制状态空间，让普通观点视频先获得稳定下限，再按解释需要增加连续结构
- 让最终像素审查与程序检查分离，避免“工具通过”被误写成“成片通过”

## 分层

### Orchestration

`SKILL.md` 只负责：触发范围、阶段顺序、Gate、失效规则、停止条件和交付报告。

### Creative References

`references/` 负责单一领域知识。每个文件只回答一类问题，避免重复全局规则。

### Motion Patterns

`resources/motion-patterns/` 负责语义拓扑到视觉状态链的映射，不包含 TTS、字幕、引擎命令和全局 QC。

### Machine Contracts

`schemas/` 描述可以被程序验证的数据。Markdown 产物负责人工可读创作决策，JSON 产物负责确定性执行。

`render-plan.json` 是执行阶段唯一真源：音频 cue、背景 token、字幕外观、页面边角信息和复杂度预算都由它传入引擎。组件内出现第二套时间或样式即属于架构违约。

### Production Profiles

`page-isolated` 是 3 分钟内观点口播和知识讲解的默认剖面：一页一个判断，旧页状态退出，不保留内容对象。`continuous-diagram` 只用于跨场对象变换本身承担解释任务的场景，并限制为一个跨场锚点。

剖面限制的是状态空间，不限制视觉质量。设计应集中在构图、层级、对比和信息出现顺序，而不是靠跨场残影与对象数量制造复杂感。

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
- pixel-audit

Markdown 负责解释和审阅；JSON 负责时间、事件和渲染。

## 验证层级

1. `scripts/validate_project.py --project <project>`：渲染前检查单一真源、hash、背景一致性、页面边角、字幕外观、复杂度预算、跨场残留和时间轴。
2. 引擎自身检查：语法、运行时、布局、运动和对比度。
3. `scripts/validate_project.py --project <project> --final final.mp4`：读取最终媒体并要求 `qc/pixel-audit.json` 中四项最终像素审查均为 `PASS`。

三层结论不得互相代替。

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
