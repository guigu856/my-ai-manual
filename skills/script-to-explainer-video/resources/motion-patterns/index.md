# 动效类型资源索引

Pattern 负责描述某类语义关系如何转成视觉状态链。它不是现成模板，也不替代叙事、分镜、字幕、音频和全局 QC。

## 四层路由

不要直接从一句话跳到某个动效模板。按以下顺序判断：

### 1. Visual Job

当前画面要完成什么：

- orient
- concretize
- explain
- compare
- prove
- emphasize
- reframe
- transition
- breathe

### 2. Representation

使用什么表达形式：

- kinetic-type
- diagram
- object-metaphor
- data-visualization
- interface
- example-scene
- image-or-broll

### 3. Semantic Topology

内容内部是什么关系：

- linear-chain
- causal-chain
- comparison
- hierarchy
- enumeration
- cycle-feedback
- state-transformation
- accumulation-decay
- merge-split

### 4. Motion Behavior

状态之间怎样变化：

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

路由结果示例：

```yaml
visual_job: reframe
representation: diagram
semantic_topology: state-transformation
motion_behavior: [compare, replace, focus]
```

## Pattern 索引

| Topology | 文件 | 适用内容 |
|---|---|---|
| linear-chain / causal-chain | [concept-chain.md](concept-chain.md) | 输入→处理→输出、原因逐步传导、关系依次建立 |
| comparison | [comparison.md](comparison.md) | 两种方法、前后状态、旧认知与新认知的共享维度对照 |
| hierarchy | [hierarchy.md](hierarchy.md) | 总体到局部、系统到模块、概念分层 |
| cycle-feedback | [cycle-feedback.md](cycle-feedback.md) | 观察→决策→执行→反馈等回流机制 |
| state-transformation | [state-transformation.md](state-transformation.md) | 同一对象从旧状态转为新状态、认知重构、角色替换 |

未匹配时先在 `STORYBOARD.md` 中自定义状态链，不要为了使用已有 Pattern 强行改变脚本。

## Pattern 文件契约

每个 Pattern 只包含：

- id / name / version
- 适用语义
- 不适用边界
- 节点或对象模型
- 推荐空间结构
- 状态链
- 连续性规则
- 主要风险
- Scene 级验收点

以下全局规则不在 Pattern 中重复：

- 音频主时钟
- 字幕系统
- 引擎实现细节
- 媒体技术检查
- 全局 QC 产物

对应规则分别读取 `references/`。

## 组合规则

一个 Scene 优先使用一个主 topology。确有必要时可组合，但必须说明主次：

```yaml
primary_pattern: comparison
secondary_pattern: state-transformation
```

组合不得同时引入多个主要注意中心。复杂 Scene 可以拆成多个 State，而不是堆叠多个模板。

## 新增 Pattern

新增前先确认：

1. 它表达的是新的语义拓扑，而不是新的视觉皮肤。
2. 现有 Pattern 通过参数化无法覆盖。
3. 至少有两个不同脚本场景可复用。
4. 能定义稳定 State 和可验证风险。

视觉颜色、字体、圆角和质感属于 style preset，不应创建成新的 motion pattern。
