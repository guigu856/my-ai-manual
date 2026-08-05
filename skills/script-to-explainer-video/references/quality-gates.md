# 质量验收 Gate

验收目标不是证明视频“能渲染”，而是确认叙事、画面、时间和媒体文件共同成立。

## Gate A：叙事

逐 Scene 检查：

- 当前画面是否服务正在说的 Beat
- 是否帮助理解，而不是只提供相关氛围
- 是否提前泄露下一段结论
- 是否存在可以删除而不损失理解的 Scene
- 视觉隐喻是否准确，有无误导
- 结论、反例和边界是否被完整表达

阻断项：画面与口播含义冲突、关键 Beat 无视觉承载、证据被错误可视化。

## Gate B：时序

检查：

- Scene 区间覆盖对应音频 cue
- State 在其语义被说到时才出现
- Event 不明显早于关键词
- 字幕与 Spoken Unit 对齐
- 转折、重点和结论有合理 hold
- 不存在口播结束后画面仍在解释上一观点

阻断项：字幕错位、画面提前剧透、动画落点与语义相反、旧时间轴被继续使用。

## Gate C：空间与视觉

检查：

- 文字是否越界、裁切或过小
- 字幕是否进入平台 UI 区
- 节点、连线、标签是否相互穿透
- z-index 和遮挡是否正确
- 跨场元素是否漂移或瞬移
- 色彩语义是否一致
- 同一时刻是否存在多个主要焦点

阻断项：关键文字不可读、主体被遮挡、关系线连接错误、元素出画。

## Gate D：技术

检查：

- 成片尺寸、fps、时长符合计划
- 视频和音频流存在且可解码
- 音频总时长与容器时长一致
- 无缺失字体、图片、音频和视频资源
- 无黑帧、透明帧或渲染异常
- 输出文件可从头到尾播放
- 渲染使用当前 `audio_hash` 和 storyboard hash

## 三级检查策略

### 1. 程序检查

覆盖完整媒体和所有帧可自动验证的内容：

- ffprobe 媒体参数
- 资源存在性
- NaN/Infinity 和非法样式值
- 文字边界和安全区（能够检测时）
- 黑帧、冻结帧和异常透明度
- schema 与 hash

### 2. 状态抽检

每个 Scene 至少检查：

- 入场前/入场帧
- 第一个稳定 State
- 变化中点
- 最终稳定 State
- 退场或跨场交接帧

生成接触表，并在报告中标明对应 Scene、State 和时间。

### 3. 风险区密集检查

只对高风险区间做逐帧或高频抽帧：

- 多对象重组
- 连线绘制和端点移动
- 遮罩、裁切和复杂转场
- 字幕与主体空间冲突
- 跨场共享对象
- 快速节奏下的多个连续 Event

不要求人类肉眼查看视频的每一帧；程序负责全量，人类/Agent 集中检查语义状态和风险区。

## 产物

`qc/qc-report.md` 至少包含：

```markdown
# QC Report

- storyboard_hash:
- audio_hash:
- render_plan_hash:
- final_file:
- duration:
- resolution:
- fps:

## Narrative
- PASS / FIX / BLOCK

## Timing
- PASS / FIX / BLOCK

## Spatial
- PASS / FIX / BLOCK

## Technical
- PASS / FIX / BLOCK

## Known limitations
```

附带：

- `contact-sheet.png`
- `probes.json`
- 风险区帧图或短片段

任何一项为 BLOCK 时不得交付。
