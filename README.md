# My AI Manual

用于集中管理 AI 辅助开发、知识视频生产与内容创作相关的 Rules 和 Skills。

## 目录结构

```text
my-ai-manual/
├── rule/
├── skills/
│   ├── ai-tip-short-video/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── four-act-motion-playbook.md
│   │       ├── remotion-implementation.md
│   │       ├── series-design-system.md
│   │       └── four-act-script.md
│   ├── idea-to-platform-content/
│   ├── idea-to-x-content/
│   ├── idea-to-xiaohongshu-post/
│   ├── social-content-publisher/
│   ├── explainer-video-review/
│   ├── video-reference-breakdown/
│   └── script-to-explainer-video/
└── README.md
```

## Rules

### `rule/代码编写规范.md`

覆盖：当前行为与最终形态、模块职责与边界、契约与命名、死分支与双路径清理等。

### `rule/文档编写规范.md`

覆盖：架构陈述、接口、验收、设计红线与文档表达约束等。

## Skills

### `skills/ai-tip-short-video/`（v1.1）

将日常 AI 使用感悟与技巧做成 **45–90 秒抖音竖屏技巧短视频**。

- **自包含**：不依赖仓库内其他 Skill，仅凭本目录即可执行
- **四段式**：共鸣 → 问题本质 → 解决方案概要 → 反问互动
- **视频内零私域**：进群/资料引导只写在 `PUBLISH.md`
- **动效强制路由**：`references/four-act-motion-playbook.md` 按段落给出允许配方（A1–D2），禁止自由发挥；方案段条数/顺序必须与口播一致
- **Remotion**：`references/remotion-implementation.md` 写明帧驱动、clamp、Sequence、安全区、禁止 CSS 动画等
- **系列视觉**：`references/series-design-system.md`
- **口播**：`references/four-act-script.md`

### `skills/idea-to-platform-content/`

想法 → 指定平台与作品形态的可用文稿/脚本。

### `skills/idea-to-x-content/`

想法 → 可发布的 X/Twitter 高密度内容。

### `skills/idea-to-xiaohongshu-post/`

想法 → 小红书静态图文作品包。

### `skills/social-content-publisher/`

作品包发布到社交平台，并做提交前核验与回读。

### `skills/script-to-explainer-video/`

观点/讲解稿 → 概念动效讲解视频（独立 Skill，与 ai-tip-short-video 无安装依赖关系）。

### `skills/explainer-video-review/`

已渲染讲解类视频的成片审查。

### `skills/video-reference-breakdown/`

把本地视频、链接或平台分享文本自动处理成普通用户可读的视频参考拆解报告。

- `SKILL.md`：来源识别、下载、媒体探测、抽帧、声音分析、补充取证、DOCX 生成与页面验收主流程
- `scripts/`：来源固化、真实媒体证据生成、重点区间加密抽帧和报告合同验证
- `references/`：画面、声音、证据语言和四部分报告细则
- `templates/report-outline.md`：固定四部分写作骨架
- `evals/` 与 `tests/`：触发边界、真实 FFmpeg 流程和报告结构验证

报告固定包含“这条视频是怎么立起来的”“它用了什么素材和音乐”“它怎么一段段剪出来的”“如果重新做一条，应该学什么”四部分，不要求读者理解内部分析模型术语，也不承担视频复刻和成片质量审查。

## 使用方式

1. 按任务加载对应 Rule / Skill，先读该 Skill 的 `SKILL.md`。
2. 执行到具体阶段再读对应 `references/`。
3. 不把全部资料一次性塞进上下文。
4. 项目产物留在各自工作目录，不提交进 Skill 包。

## 内容维护

- Rule：跨 Skill 通用约束
- Skill 主文件：编排与不可违反契约
- Reference：单一领域知识，避免无必要交叉依赖
- 项目输出不进 Skill 包
