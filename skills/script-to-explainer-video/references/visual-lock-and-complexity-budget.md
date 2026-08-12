# 视觉锁与复杂度预算

## 全局视觉锁

分镜锁定后，在 `render-plan.json.style_lock` 固定：

- `color_mode`：`dark`、`light` 或 `mixed-intentional`。
- `background_token`：全片默认背景 token。
- `caption`：背景框、描边、阴影、位置和安全区。
- `page_chrome`：左上角分类标签、右上角页码和主标题是否必需。

当 `color_mode` 不是 `mixed-intentional` 时，每个 Scene 必须使用同一个 `background_token`。确需明暗切换时，逐 Scene 写清切换的叙事作用；“增加变化”不是充分理由。

## 页面边角信息

`page_chrome` 默认要求每个 Scene 同时具备：

- 左上角 `corner_label`：当前段落角色或问题类型。
- 右上角 `page_number`：`当前页 / 总页数`。
- `headline`：当前唯一主判断。

最终检查不是只搜字符串，而是检查：

- 元素存在且非空。
- 最终编码帧中可见。
- 位于安全区内。
- 三者互不重叠。
- 字号、位置和色彩在全片保持同一语法。

## 字幕视觉锁

默认字幕：

```json
{
  "background": "none",
  "background_alpha": 0,
  "outline_px": 0,
  "shadow": false,
  "max_lines": 1
}
```

用户明确要求字幕框、描边或阴影时再修改。最终 MP4 至少抽取浅背景、深背景、长字幕和场景边界四类帧。源 CSS/ASS 看起来正确不构成通过证据。

## 复杂度预算

默认每个 Scene：

- `max_focal_points = 1`
- `max_content_groups = 4`
- `max_simultaneous_text_blocks = 4`
- `max_primary_motion_relations = 1`
- `max_persistent_elements = 0`（`page-isolated`）或 `1`（`continuous-diagram`）

内容组指观众需要分别理解的卡片、节点群、比较面板或文字区，不按 DOM 节点数量机械计算。

超出预算时按顺序处理：

1. 删除不承担理解任务的装饰。
2. 把同时出现改为按语义逐项出现。
3. 拆成两个页面隔离 Scene。
4. 仍超限时回到分镜，不在实现层用缩小字号、降透明度或叠放解决。

## 禁止用视觉补丁掩盖上游问题

- 旧对象应退出时，不使用 `opacity: 0.06` 假装清理。
- 标题抢跑时，修改 cue 绑定，不用延迟整场动画掩盖。
- 字幕框违约时，修改统一字幕配置并整片重渲染，不逐帧覆盖。
- 风格不统一时，修正 `style_lock` 和 Scene token，不在 CSS 末尾追加覆盖规则。
