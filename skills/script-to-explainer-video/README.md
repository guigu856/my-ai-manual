# script-to-explainer-video

> 将口播脚本或观点文案变成以配音为主时钟的概念动效解说视频。

## 适用场景

- 从口播脚本制作配音、字幕和程序化概念动效
- 用 `timeline.json` 统一驱动 Remotion 或 HyperFrames
- 修复已有工程中的音画、字幕和场景时序问题
- 将渲染成片交给 `explainer-video-review` 做后渲染审查

## 不适用场景

- 只改写文案或标题
- 只给已有视频加字幕
- 编辑实拍素材或拆解参考视频
- 只审查最终 MP4

## 安装与验证

本仓库是多个 Skill、Rule 和 Agent 资料的集合；本 Skill 位于 `skills/script-to-explainer-video/`。

```bash
npx skills add guigu856/my-ai-manual --skill script-to-explainer-video
```

在项目目录执行时间轴检查：

```bash
python skills/script-to-explainer-video/scripts/validate_timeline.py --project <project-dir>
```

## 主要产物

- `segments.json`：冻结后的语义分段
- `timeline.json`：帧率、段落区间和句级 cue
- `audio/`：最终配音
- `remotion/src/` 或 `hyperframes/`：动效实现
- `out/final.mp4`：可播放成片
- `out/captions.srt` 或 `out/captions.vtt`：字幕
- `out/production-handoff.json`：交接给审查 Skill 的证据入口

## 直接触发示例

- “把这段口播做成极简概念动效视频。”
- “用配音 cue 驱动字幕、场景和转场。”
- “修复这个 Remotion 工程的时间轴和字幕同步。”

## 验收边界

生产阶段负责音频、时间轴、动效、渲染和前置检查。成片的视觉表达、空间连贯、时序对齐和字幕可读性审查交给 `explainer-video-review`。没有真实渲染或人工审查证据时，报告中标记 `missing_evidence`。

## 依赖

- Node.js 与 npx
- Python 3.9+
- Remotion 或 HyperFrames 工程
- 发布级检查需要 FFmpeg 与 ffprobe
## 你可以直接这样说

- “把这段口播做成概念动效视频。”
- “先按配音生成 timeline.json，再做 Remotion 动效和字幕。”
- “修复这个视频工程的音画同步，并准备交给审查 Skill。”

## Package validation

```bash
python scripts/validate_skill.py <skill-dir>
python scripts/trigger_eval.py <skill-dir> --cases <skill-dir>/evals/trigger_cases.json
```

## Troubleshooting

| 问题 | 检查项 |
|---|---|
| Skill 没有触发 | 检查请求是否同时包含脚本/工作流、制作动作和解说视频目标 |
| 字幕或动效漂移 | 检查是否存在第二套时间轴，统一回到 `timeline.json` |
| 时间轴校验失败 | 运行 `validate_timeline.py`，先修复段落或 cue 数据 |
| 成片审查出现问题 | 修复源文件后整片复渲，再把新 MP4 和证据交给 `explainer-video-review` |