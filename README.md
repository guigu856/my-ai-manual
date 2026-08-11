# My AI Manual

用于集中管理 AI 辅助开发、知识视频生产与内容创作相关的 Rules 和 Skills。

## 目录结构

```text
my-ai-manual/
├── rule/
│   ├── 1.md
│   ├── 2.md
│   ├── 3.md
│   ├── 4.md
│   ├── 代码编写规范.md
│   └── 文档编写规范.md
├── skills/
│   ├── idea-to-platform-content/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── writing-methodology.md
│   │       ├── formats/
│   │       └── platforms/
│   ├── idea-to-x-content/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── value-diagnosis.md
│   │       ├── format-routing.md
│   │       └── human-writing.md
│   ├── idea-to-xiaohongshu-post/
│   │   ├── SKILL.md
│   │   ├── README.md
│   │   ├── agents/
│   │   ├── evals/
│   │   ├── references/
│   │   ├── reports/
│   │   ├── scripts/
│   │   └── templates/
+│   ├── social-content-publisher/
+│   │   ├── SKILL.md
+│   │   ├── README.md
+│   │   ├── agents/
+│   │   ├── evals/
+│   │   ├── references/
+│   │   ├── reports/
+│   │   ├── scripts/
+│   │   ├── templates/
+│   │   └── tests/
│   └── script-to-explainer-video/
│       ├── SKILL.md
│       ├── DESIGN.md
│       ├── references/
│       │   ├── narrative-design.md
│       │   ├── script-decomposition.md
│       │   ├── visual-design-principles.md
│       │   ├── storyboard-contract.md
│       │   ├── audio-and-timing.md
│       │   ├── caption-system.md
│       │   ├── motion-language.md
│       │   ├── engine-routing.md
│       │   └── quality-gates.md
│       ├── resources/
│       │     
│       │   
│       │   
│       │       
│       │       
│       │       
│       │       
│       │       
│       ├── schemas/
│       │   ├── brief.schema.json
│       │   ├── audio-meta.schema.json
│       │   
│       ├── templates/
│       │   
│       │   
│       
└── README.md
```

## Rules

### `rule/代码编写规范.md`

覆盖：

- 当前行为与最终形态
- 模块职责、显式依赖与边界
- 契约、类型、默认值、命名和文档同步
- 死分支、双路径、残留状态与多余兜底的清理标准

### `rule/文档编写规范.md`

覆盖：

- 架构陈述、接口定义、任务分解和验收标准
- 设计红线、禁止项与已验证技术参数
- 文档定位、表格和列表的表达约束
- 文档内容的最终形态规范

## Skills

### `skills/idea-to-platform-content/`

将想法、观点或初步文稿转化为指定平台、指定作品形态的可直接使用文稿 / 脚本。

- `SKILL.md`：触发条件、核心工作流（确认平台与作品形态 → 提炼观点 → 结构推进 → 适配 → 自检）、路由与边界
- `references/writing-methodology.md`：跨平台通用写作方法论（观点提炼、主线纪律、信息增量、自然度与去 AI 味、修改自检）
- `references/formats/`：作品形态规范（口播短视频、非口播画面驱动视频、图文/知识卡/工具卡、推文/Thread、长文）
- `references/platforms/`：平台约束（抖音、小红书、X/Twitter），易变参数标注为需刷新

### `skills/idea-to-x-content/`

将一个想法、观点、碎片化表达、文案或脚本转化为可直接发布到 X/Twitter 的高信息密度内容。

- `SKILL.md`：观点还原 → 价值诊断 → 结构路由 → 主帖/回复展开 → 去 AI 味 → 发布前检查
- `references/value-diagnosis.md`：判断观点是否具备非显而易见、纠偏、痛点、机制、边界或方法价值，并从原始表达中挖掘隐藏价值
- `references/format-routing.md`：按内容结构与账号限制自适应选择单条、主帖+回复链、Thread、清单式推文或脚本拆解式 Thread
- `references/human-writing.md`：保留作者语气，删除机械对仗、空洞拔高、无来源群体断言、强迫整齐和其它常见 AI 写作痕迹

### `skills/idea-to-xiaohongshu-post/`

把想法、观点、文章、脚本或已有文案转成可直接发布的小红书静态图文作品包。

- `SKILL.md`：来源合同 → 内容路由 → 拆页 → 文案 → 视觉生产 → 渲染 → 发布门禁
- `references/`：内容类型、卡片叙事、视觉渲染和质量门禁
- `scripts/validate_xhs_package.py`：检查标题正文、卡图数量、连续命名、PNG 尺寸、预览和来源记录
- `evals/`：触发边界和输出评估规格
- `reports/`：先例研究、Skill IR、触发报告和创建交接
- `templates/`：工作简报示例

### `skills/social-content-publisher/`

把已经完成的图文或视频作品包发布到社交平台，并在提交后回读线上标题、正文和媒体，避免“命令成功、内容乱码”。

- 当前已验证：小红书静态图文的登录校验、UTF-8 预检、发布、线上回读和原笔记修复
- 当前已预留：小红书视频、抖音图文 / 视频、快手图文 / 视频、Bilibili 视频、视频号和 YouTube。
- `scripts/preflight_manifest.py`：检查编码、CJK、媒体、标题限制、秘密字段和重复发布意图
- `scripts/publish_social.py`：dry-run 与提交入口；中文通过 UTF-8 文件和 Python 参数列表传递
- `scripts/verify_xiaohongshu_note.py`：从管理页和编辑页回读线上内容
- `scripts/repair_xiaohongshu_note.py`：编辑原笔记并重新核验，不默认重复发布

### `skills/script-to-explainer-video/`

把观点、想法、讲解稿或口播脚本转换成概念动效讲解视频。

- `SKILL.md`：只保留入口、核心原则、阶段 Gate、失效规则和交付契约
- `references/`：叙事、脚本、视觉、分镜、音频、字幕、动效、引擎和 QC 细则
- `resources/motion-patterns/`：不同语义拓扑的可复用视觉状态模型
- `schemas/`：机器可验证的阶段数据契约
- `templates/`：BRIEF、SCRIPT 和 STORYBOARD 示例
- `DESIGN.md`：维护者阅读的架构边界和扩展规则

生产流程：

```text
BRIEF
→ SCRIPT
→ STORYBOARD
→ FINAL AUDIO + CUES
→ RENDER PLAN
→ REMOTION / HYPERFRAMES
→ QC
→ FINAL MP4
```

最终音频只在叙事和分镜锁定后生成；通过音频验收后，实测 cue 才成为执行阶段唯一主时钟。

## 使用方式

1. 根据任务加载对应 Rule。
2. 激活对应 Skill 并先读取 `SKILL.md`。
3. 执行到具体阶段时，再读取该阶段的 reference、pattern、schema 或 template。
4. 不把全部资料一次性塞入 Agent 上下文。
5. 交付前完成叙事、时序、空间和技术四层验收。

## 内容维护

- Rule 维护跨 Skill 的通用约束。
- Skill 主文件维护编排流程和不可违反的主契约。
- Reference 维护单一领域知识，不跨文件重复全局规则。
- Motion Pattern 只描述语义拓扑、状态链和局部风险，不承担字幕、音频或全局 QC。
- Schema 维护机器数据结构。
- Template 提供示例，不作为硬编码默认答案。
- 项目输出文件保留在各自项目工作目录，不提交进 Skill 包。

