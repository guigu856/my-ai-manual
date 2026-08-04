# 意图、输入输出与边界契约

## 目标任务

把一份口播脚本、观点文案或概念 brief 变成可观看的中文概念动效解说视频。画面表达概念之间的关系，配音和字幕承载叙述，时间轴由配音实测结果驱动。

## 输入

| 输入 | 必需 | 说明 |
|---|---:|---|
| 口播脚本或观点文案 | 是 | 没有可冻结的文本时，任务停在意图收敛阶段 |
| 目标平台/画布 | 否 | 未提供时按 16:9 处理 |
| 声线或配音方式 | 否 | 未提供时按脚本气质选择，并以试听结果为准 |
| 视觉风格 | 否 | 未提供时使用深色极简、底色加双语义色 |
| Remotion/HyperFrames 工程 | 否 | 已有工程优先沿用；新工程由执行环境决定 |
| 外部媒体、BGM、字体 | 否 | 只使用用户提供或已确认来源的资源 |

## 输出

生产阶段至少留下：

```text
project/
├── segments.json
├── timeline.json
├── audio/
├── remotion/src/ 或 hyperframes/
└── out/
    ├── final.mp4
    ├── captions.srt 或 captions.vtt
    └── production-handoff.json
```

`production-handoff.json` 至少记录：

```json
{
  "skill": "script-to-explainer-video",
  "segments": "segments.json",
  "timeline": "timeline.json",
  "audio": "audio/final.wav",
  "video": "out/final.mp4",
  "captions": "out/captions.srt",
  "production_checks": "pass",
  "review_skill": "explainer-video-review",
  "review_status": "pending"
}
```

## 默认值与阻塞条件

默认值可以直接执行：比例、帧率、风格、分段数量和 BGM 选择都按主 Skill 处理。以下情况才构成阻塞：

- 没有脚本，也没有可用的文字输入
- 用户要求沿用一个不存在的工程或资源
- 目标输出与现有工程能力冲突，且没有替代路径
- 用户要求使用的素材来源、字体或声音权限状态不清楚

## 文稿冻结规则

1. 每段表达一个完整观点，默认 1–3 句。
2. `title` 是短点题词或模块名，不承担整句叙述。
3. 文稿强化只在冻结前完成；冻结后字幕与画面引用冻结稿原文。
4. 抽象论断需要具体例证时，例证写入冻结稿，不在动画阶段临时补写。

## 相邻 Skill 交接

- `script-to-explainer-video`：脚本、音频、时间轴、动效、渲染和生产检查。
- `explainer-video-review`：对已渲染 MP4 做视觉表达、空间一致、时序对齐和字幕可读性审查。
- 审查发现的问题回传到源文件、布局数据或 cue 数据；生产 Skill 负责修复和整片复渲。

审查 Skill 是仓库中的另一个独立 Skill，不把它的四维审查清单复制进生产入口。