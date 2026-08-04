# Explainer Video Review

对已经渲染的口播或概念动效视频做可复核的 post-render audit。它检查视觉表达、空间连续、时序对齐、字幕可读性和技术完整性，输出带证据引用的问题报告与生产修复交接。

## 安装

```bash
npx skills add guigu856/my-ai-manual --skill explainer-video-review
```

## 适用请求

### 你可以直接这样说

- “审查这个概念动效视频成片，输出时间戳问题清单。”
- “检查 MP4 的字幕、音画同步、转场和空间连贯性。”
- “根据 timeline.json 复核成片，并生成 review-report.json。”
- “找出这个知识视频的 blocker、major、minor 问题并给修复建议。”

### 触发边界

输入已经渲染的 MP4 或可读取的成片视频时触发。新建脚本到视频、口播改写、已有实拍素材剪辑和参考视频分析分别由其他 Skill 处理。

## 审查输出

- `review-manifest.json`：媒体指纹、审查基准、采样档位和证据范围
- `review-report.json`：四维结果、问题 ID、时间戳、严重级、置信度和修复建议
- Markdown 或聊天内摘要
- 生产 Skill 的修复交接：源文件修复、整片重渲染、复审条件

## 审查档位

- `quick`：首轮体检和短片
- `standard`：默认交付审查
- `dense`：快速动效、复杂转场和音画争议

抽样频率由媒体时长和动效密度自动选择；用户可以覆盖。声音相关问题必须同时核对音频窗口和画面证据。

## 前置条件

- Python 3.10+
- `ffprobe` / `ffmpeg` 用于媒体结构和音频窗口检查
- 可选：冻结文稿、`segments.json`、`timeline.json`、字幕、最终配音和制作要求

## 验证

```bash
python C:/Users/32249/.codex/skills/qiaomu-meta-skill/scripts/validate_skill.py .
python C:/Users/32249/.codex/skills/qiaomu-meta-skill/scripts/trigger_eval.py . --cases evals/trigger_cases.json --output reports/trigger-eval.json
python scripts/validate_review_report.py --input examples/review-report.valid.json
python scripts/build_sample_plan.py --duration 42.8 --preset standard
python -m unittest discover -s tests -p "test_*.py" -v
```

## Troubleshooting

| 情况 | 处理 |
|---|---|
| 没有冻结文稿或时间轴 | 继续做可观察审查，并把缺口写入 `missing_evidence` |
| 没有音频流 | 时序和字幕对位维度标记为 `missing_evidence` |
| 快速动效漏检 | 切换 `dense`，增加 cue 边界和连续帧采样 |
| 报告校验失败 | 先修复字段、时间戳、finding ID 和证据引用，再交接 |
| 发现源文件问题 | 交给 `script-to-explainer-video`，修复后整片重渲染并复审 |

## 相关 Skill

- 生产：[`script-to-explainer-video`](../script-to-explainer-video/SKILL.md)
- 审查规则：[四维检查规则](references/four-dimensions.md)
- 报告契约：[审查契约、报告和状态](references/review-contract.md)
