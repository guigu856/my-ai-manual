# Remotion 实现硬约束（AI Tip Short Video）

本文件提炼自：

- 官方 `remotion-dev/skills`（remotion-best-practices / markup）
- 社区 `BayramAnnakov/remotion-video-director`
- 本仓库 `script-to-explainer-video` 的 engine-routing 与 motion-language
- 常见生产踩坑（CSS 动画不渲染、frame 相对性、未 clamp、硬切静止元素等）

Agent 在编写或修改 Remotion 代码时必须遵守，禁止凭空发明相反做法。

## 1. 动画驱动

- **唯一合法驱动**：`useCurrentFrame()` + `interpolate()` 或 `spring()`。
- **优先** `interpolate()`；仅当明确需要物理感时使用 `spring()`。
- **禁止**：CSS `transition` / `animation`、Tailwind `animate-*`、`requestAnimationFrame`、`Date.now()`、`Math.random()` 驱动视觉。
- 原因：上述方式在 Remotion 服务端/逐帧渲染中不可复现或根本不生效。

```tsx
const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const opacity = interpolate(frame, [0, 0.4 * fps], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

## 2. Clamp 与外推

- 所有 `interpolate` **必须**设置 `extrapolateLeft: "clamp"` 与 `extrapolateRight: "clamp"`（或等价明确外推策略）。
- 禁止依赖默认外推导致文字飞出画面或透明度变负。

## 3. Sequence 与 frame 相对性

- `useCurrentFrame()` 返回的是**相对最近 `<Sequence>` 的局部帧**，不是全局时间轴。
- 跨场景时间请用 `<Sequence from={...} durationInFrames={...}>` 组合，而不是在子组件里手动减全局偏移（易错）。

## 4. 入场纪律

- 每个关键元素必须有入场动画（opacity / translate / scale 等）。
- **禁止**场景硬切后文字已完整静止出现（「突然蹦字」）。
- 系列内统一：短 ease-out 入场（约 8–12 帧）或统一 cross-dissolve（8–12 帧）。选定后写入 style_lock，全片一致。

## 5. Transform 写法

- 优先在 `style` 中使用独立属性：`scale`、`translate`、`rotate`（便于 Studio 与插值）。
- 避免难以插值的巨型 `transform` 字符串拼接（除非必要且已验证）。

## 6. 资源与字体

- 静态资源放 `public/`，用 `staticFile()` 引用。
- 中文字体必须显式加载并在渲染环境可用；禁止假设系统字体在 CI/无头环境一致。

## 7. 时间真源

- 场景起止、字幕、动画事件的时间来自分镜/render 计划或音频 cue，**禁止**在多个组件内硬编码互相矛盾的秒数。
- 时长变更时只改一处配置（theme 或 timeline 常量），再映射到 Sequence。

## 8. 竖屏安全区（9:16）

- 关键文字避开底部约 15%（平台 UI/字幕条）。
- 左右保留足够 padding（建议 ≥ 64px @1080 宽）。
- 标题字号需在手机预览下仍清晰；避免长句挤在一行。

## 9. 搭建与渲染命令

- **禁止**依赖会弹出交互向导的命令作为唯一路径（如无参数的 `npx create-video` / 无 composition 的 `npx remotion render`）。
- 渲染必须显式指定入口与 composition id，例如：

```bash
npx remotion render src/Root.tsx AiTipVideo out/final.mp4 --codec=h264 --crf=18
```

## 10. Still-first

- 先导出各 Scene 稳定态静帧，确认层级、安全区、对比度，再出完整 MP4。
- 静帧已错误时，禁止靠完整渲染「碰运气」。

## 11. 与动效语言的衔接

- 动作选择仍遵循 `motion-language.md`：reveal / focus / accumulate / replace 等语义动作。
- 本系列默认以 **reveal + focus + hold** 为主；少用复杂 connect/loop，除非方案段需要步骤关系。
- 每个 Beat 最多一个主要强调手段（字号、颜色或短暂停顿）。

## 12. 禁止清单（汇总）

- CSS/Tailwind 动画驱动画面
- 未 clamp 的 interpolate
- 无入场的硬切文字
- 组件内散落绝对秒数且与分镜不一致
- 底部安全区被大字或卡片占用
- 为「好看」添加的持续漂浮/随机抖动
- 在视频组件内写进群/领资料文案
