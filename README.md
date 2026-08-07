# My AI Manual

用于集中管理 AI 辅助开发、知识视频生产与内容创作相关的 Rules 和 Skills。

## 目录结构

```
my-ai-manual/
├── rule/
│   ├── 1.md                 # 基础行为准则
│   ├── 2.md                 # 命名与文档规范
│   ├── 3.md                 # 项目结构规范
│   ├── 4.md                 # 代码逻辑与质量规范
│   ├── 代码编写规范.md       # 代码的最终形态、边界与契约规范
│   └── 文档编写规范.md       # 文档的最终形态与内容边界规范
├── skills/
│   ├── idea-to-platform-content/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── writing-methodology.md
│   │       ├── formats/
│   │       └── platforms/
│   └── script-to-explainer-video/
│       ├── SKILL.md
│       ├── resources/
│       │   └── motion-patterns/
│       │       ├── index.md
│       │       └── concept-chain.md
│       └── scripts/
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

### `skills/script-to-explainer-video/`

将口播脚本转换为概念动效解说视频。

- `SKILL.md`：生产方法、音频主时钟、字幕、空间结构、转场和质量验收
- `resources/motion-patterns/index.md`：动效类型索引、选择规则和资源契约
- `resources/motion-patterns/concept-chain.md`：线性概念链路与关系重组类型
- `scripts/`：可执行辅助脚本

Skill 的通用方法和跨类型约束写入 `SKILL.md`，具体视觉类型写入 `resources/`。

## 使用方式

1. 根据任务加载对应的 Rule 文件。
2. 根据任务类型加载对应的 Skill。
3. 先读取 Skill 主文件，再读取匹配的资源文件。
4. 按文件中的输入、流程、约束和验收标准执行。
5. 交付前完成对应的结构检查、渲染检查和产物验证。

## 内容维护

- Rule 文件维护通用约束。
- Skill 主文件维护生产方法和跨类型规则。
- Resource 文件维护可替换的具体方案。
- 项目输出文件保留在各自项目工作目录中。
