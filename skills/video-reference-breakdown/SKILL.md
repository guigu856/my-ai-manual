---
name: video-reference-breakdown
description: 拆解和分析参考视频，自动处理本地文件、视频链接或平台分享文本，下载并固化视频，读取真实媒体信息，抽帧、生成联系表、分析声音、补充重点区间证据，最终交付普通用户也能看懂的五章 DOCX 拆解报告。用户说“拆解这个视频”“分析参考片”“看看这个链接怎么剪的”“这条视频为什么好看”“提炼可复用剪法”时必须使用，即使没有点名本 Skill。视频制作、已有成片质量审查、只下载不分析、只提取字幕或只做格式转换走其他 Skill。
metadata:
  version: 1.0.0
  compatibility: 需要 Python 3.11+、FFmpeg/FFprobe；链接下载需要 yt-dlp；DOCX 生成与页面检查需要宿主文档能力。
---

# 视频参考拆解

## 交付目标

输入本地视频、链接、分享文本或对话附件，输出一份连续可读的五章 DOCX：

1. 第一章：先用一分钟看懂这条视频；
2. 第二章：音乐和声音是怎么带动视频的；
3. 第三章：画面是怎么一段段剪出来的；
4. 第四章：声音和画面是怎么配合的；
5. 第五章：如果重新做一条，应该学什么。

报告面向没有剪辑和音频工程知识的普通用户。把分析做深，把结论写得直接，不要求读者先学术语。

## 执行流程

### 1. 确认来源

- 上下文已有文件、路径、链接或分享文本：直接执行。
- 上下文没有视频来源：只询问视频文件或链接。
- 不重复询问输入属于文件还是链接，来源脚本自行识别。

为本次任务建立：

```text
output/video-reference-breakdown/<run-id>/
```

### 2. 固化视频

调用：

```powershell
python scripts/resolve_source.py "<文件、链接或分享文本>" --output-dir "<run-dir>"
```

读取 `<run-dir>/source.json`。链接下载失败时直接报告原始错误和缺少的 Cookie、代理或程序；不要把失败的链接当成已经取得的视频。

### 3. 生成第一批证据

调用：

```powershell
python scripts/analyze_media.py "<source_media.local_path>" --output-dir "<run-dir>/analysis"
```

读取 `analysis-manifest.json`，然后实际查看：

- 全部联系表；
- 场景变化候选帧；
- 波形图；
- 重要声音变化候选；
- 音乐强弱数据；
- 媒体时长、分辨率、帧率和音频流。

算法结果只负责指出可能值得观察的位置。不要仅凭候选边界、tempo 或强弱数值完成报告。

### 4. 查看画面和听取声音

按时间顺序浏览全片证据。对报告中的重要片段，检查对应原视频或分析音轨，确认：

- 主要画面是什么；
- 画面内部发生了什么变化；
- 声音在变化前、同时还是之后出现；
- 这种安排给观看带来什么效果。

观察画面时读 `references/visual-analysis.md`；分析声音时读 `references/audio-analysis.md`。

### 5. 补充证据

快速切换、遮罩、闪白、定格、转场或音画先后关系看不清时，只对明确区间调用：

```powershell
python scripts/refine_intervals.py "<video>" `
  --output-dir "<run-dir>/analysis/refined" `
  --interval "<start>:<end>" `
  --step 0.1
```

`--interval` 可重复传入。步长不得超过 0.1 秒。补充后查看新增帧，再写结论。

### 6. 编写五章内容

读：

- `references/report-contract.md`：五章标题、表格和每章要求；
- `references/evidence-and-language.md`：事实、判断、证据和通俗表达纪律；
- `templates/report-outline.md`：写作骨架。

第三章的简明时间线连续覆盖全片。普通片段使用易读粒度，复杂片段再拆细。第四章至少整理一套可以照着执行的连续剪法，不能只写“节奏感强”“转场自然”等空泛评价。

### 7. 生成 DOCX

调用宿主文档能力，将完整内容生成：

```text
<run-dir>/《视频名称》拆解报告.docx
```

文档使用清晰的封面、稳定标题层级和可跨页阅读的表格。逐镜表较宽时优先横向页面或拆分表格，不通过缩小到难以阅读的字号硬塞。

### 8. 渲染和检查

使用宿主文档能力把 DOCX 渲染为逐页 PNG，并逐页检查：

- 没有截断、重叠、乱码或破损表格；
- 五章标题完整且顺序正确；
- 第三章完整时间线可连续阅读；
- 证据编号、时间范围和把握程度没有丢失；
- 报告正文没有暴露内部术语。

然后调用：

```powershell
python scripts/validate_report.py "<report.docx>" --rendered-pages-dir "<pages-dir>"
```

修正全部错误并重新渲染。警告需要人工核对，确认报告确实包含相应信息后才能交付。

## 用户可见表达

重要结论依次写：

```text
实际看到或听到了什么
我们的分析判断是什么
判断依据是什么
把握程度：高 / 中 / 低
```

正文使用“音乐段落”“重要声音变化”“主要画面”“画面里的变化”“声音和画面的配合”“可以重复使用的剪法”等普通表达。

正文不出现：

```text
MusicSection / MusicLayer / AudioEvent / EnergyCurve
RhythmUnit / MainShot / InShotEvent
AudioVisualBinding / EditingSentence
algorithm_candidate / agent_inference
```

## 事实边界

- 时长、时间戳、帧、波形、响度和文件哈希是可验证事实。
- 剪辑意图、观看作用、情绪解释和复用方法是分析判断。
- 不猜测创作者心理、所用软件、插件、隐藏图层或具体效果参数。
- tempo、beat、场景变化和声音事件在 Agent 确认前只是候选。
- 证据不足时降低把握程度或补充取证，不用顺口但缺少依据的说法填空。

## 边界

- 本 Skill 负责参考片拆解与五章报告，不负责复刻、剪辑或渲染一条新视频。
- 本 Skill 不审查用户自己生成的成片质量；质量审查使用 `explainer-video-review` 等对应 Skill。
- 用户只要求下载时，直接使用下载工具，不启动完整拆解。
- 本 Skill 不建立知识库，不输出 Plugin 的“待沉淀知识”第六章。
- 中间媒体和证据留在任务输出目录，不写入 Skill 安装目录。
