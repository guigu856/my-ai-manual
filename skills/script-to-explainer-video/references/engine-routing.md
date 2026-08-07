# 引擎路由与适配契约

主 Skill 只定义创作和渲染计划，不把 Remotion 与 HyperFrames 的全部实现细节混入入口文件。

## 选择 Remotion

优先用于：

- React/TypeScript 组件化项目
- 多种可复用 Scene 组件
- 数据驱动图表、代码、界面和复杂状态
- 需要 Zod props、`calculateMetadata` 或程序化批量渲染
- 已有 Remotion 工程或团队熟悉 React

实现要求：

- 所有时间来自 frame 和 `render-plan.json`
- 使用 `Sequence`、composition props 或统一 timeline adapter
- 禁止 `Date.now()`、随机数和浏览器实时计时器
- 媒体使用可确定加载方式
- duration 由 render plan 推导，不在多个组件中重复计算

## 选择 HyperFrames

优先用于：

- HTML/CSS/GSAP 为主的动效
- 需要 SVG、Lottie、Three.js、Anime.js 或 Web 动画组合
- 更适合按 Scene 输出独立 HTML 片段
- 需要网页式快速预览、设计系统和多运行时动效
- 已有 HyperFrames composition 或 registry 组件

实现要求：

- 使用可 seek、可重复的时间轴
- 媒体和动画受 composition 时间控制
- 不依赖页面加载后自然播放的不可控动画
- 每个 Scene 的 duration 和 cue 来自 render plan

## Adapter 输入

无论使用哪个引擎，都必须消费同一逻辑输入：

```text
BRIEF.md
SCRIPT.md
STORYBOARD.md
audio/audio-meta.json
audio/captions.json
render-plan.json
assets/
```

引擎不能重新解释叙事或静默改变 Beat、State 和 Event。

## render-plan 最小映射

Adapter 必须支持：

- canvas 与 fps
- Scene 起止帧
- State 起止帧
- Event 的 cue、offset 和 duration
- 元素身份与跨场连续性
- 字幕 cue
- 音频文件
- 资源引用
- style token

## 目录建议

### Remotion

```text
src/
├── Root.tsx
├── timeline/
│   └── adapter.ts
├── scenes/
├── components/
└── styles/
```

### HyperFrames

```text
compositions/
├── index.html
├── frames/
├── components/
└── frame.md
```

## 返工边界

- 叙事错误：回到 `SCRIPT.md`
- 视觉策略错误：回到 `STORYBOARD.md`
- cue 错误：回到音频或 render plan
- 组件实现错误：留在引擎层修复

不要通过引擎代码临时添加未经过分镜的字幕、结论或新场景。

## Still-first

正式编码后先渲染：

- 每个 Scene 的首个稳定 State
- 关键变化中点
- 最终 State
- 跨场交接帧

Still 正确后再编码完整 MP4。动态图形错误若在静态状态就存在，不应通过完整渲染反复试错。
