# Remotion 实现硬约束

本文件自包含。实现层必须遵守；违反则视为不合格交付。

约束对齐业界已验证问题：CSS 动画在逐帧渲染中不生效、未 clamp 导致飞出画面、`useCurrentFrame` 相对 Sequence 而非全局、硬切后静止蹦字、交互式 CLI 导致自动化失败等（见 Remotion 官方 Agent Skills 与常见生产实践）。

## 1. 动画驱动

- 唯一合法驱动：`useCurrentFrame()` + `interpolate()` 或 `spring()`。
- 优先 `interpolate()`；仅当需要明确物理感时用 `spring()`。
- **禁止**：CSS `transition` / `animation`、Tailwind `animate-*`、`Date.now()`、无种子随机数驱动画面。

```tsx
const frame = useCurrentFrame();
const { fps } = useVideoConfig();
const opacity = interpolate(frame, [0, 0.35 * fps], [0, 1], {
  extrapolateLeft: "clamp",
  extrapolateRight: "clamp",
});
```

## 2. Clamp

所有 `interpolate` 必须设置 `extrapolateLeft` 与 `extrapolateRight` 为 `clamp`（或等价明确策略）。

## 3. Sequence 与局部帧

`useCurrentFrame()` 相对最近 `<Sequence>`。跨段用 `<Sequence from={...} durationInFrames={...}>`，避免在子组件手写易错全局偏移。

## 4. 入场纪律

关键元素必须有入场动画。禁止场景切换后文字已完整静止出现。  
入场时长落在 playbook 参数带内（通常 8–12 帧）。

## 5. 配方实现边界

只实现 `four-act-motion-playbook.md` 中已选配方。  
不得新增 playbook 未列出的运动类型（如无限漂浮、复杂路径、无语义粒子）。

## 6. 时间真源

场景起止来自分镜/时间线配置一处；禁止多个组件硬编码互相矛盾的秒数。

## 7. 竖屏安全区（9:16）

关键文字避开底部约 15%；左右留白充足。主标题在手机预览下必须可读。

## 8. 资源与字体

静态资源放 `public/`，使用 `staticFile()`。中文字体显式加载，不假设 CI 系统字体一致。

## 9. 搭建与渲染

避免依赖会弹出交互向导的命令作为唯一路径。渲染显式指定入口与 composition：

```bash
npx remotion render src/Root.tsx AiTipVideo out/final.mp4 --codec=h264 --crf=18
```

## 10. Still-first

先导出各段稳定态静帧，确认焦点、安全区、对比度，再渲染完整 MP4。

## 11. 禁止清单

- CSS/Tailwind 动画驱动画面
- 未 clamp 的 interpolate
- 无入场硬切文字
- 视频组件内进群/领资料文案
- 方案段条数或顺序与口播不一致
- 单镜多主焦点
