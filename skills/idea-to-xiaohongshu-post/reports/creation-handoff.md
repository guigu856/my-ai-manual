# Creation Handoff

## Result

- Skill: `idea-to-xiaohongshu-post` 0.1.0
- Job: 把想法或现有材料转成包含卡图、标题、正文、预览和质检的可发布小红书图文作品包
- Owner: `guigu856`
- Maturity: Production candidate
- Publication: feature branch / PR pending

## Reference Skills Studied

- `idea-to-platform-content`：学习来源忠实、平台/形态分离、事实边界；落到 `work-brief.md`、Gate 1–4 和边界路由。
- `guizang-social-card-skill`：学习 3:4 卡片、HTML→PNG、视觉系统和移动端检查；落到 `production-and-rendering.md` 和 Gate 5–7。
- `xhs-markdown-card-collab`：学习分页、孤行、空白、真实浏览器导出检查；落到 contact sheet 和移动端 QA。
- `xhs-writer-skill`：学习完整发布包和真实素材优先；落到统一输出目录和 `post.md` / 卡图 / 预览一起交付。

## Absorbed And Rejected

- Keep: 来源忠实、逐页职责、真实浏览器渲染、移动端检查、完整发布包。
- Adapt: 抽象观点可使用功能性排版；专用卡片 Skill是视觉适配器，不接管观点合同。
- Reject: 爆款承诺、固定标题公式、全组 AI 生图、账号登录与自动发布、AGPL 模板复制。
- Invent: 三态交付、页面信息增量、标题/卡图/正文一致性门禁、无 Pillow 的 PNG 包校验器。

## Advantages And Evidence

- **Design advantage:** 一个入口同时拥有来源忠实、卡片叙事、视觉执行和发布包契约。
- **Design advantage:** `publish-ready` 需要内容、视觉、移动端和技术门禁同时通过。
- **Validated advantage:** 15/15 trigger cases 通过；包校验脚本 3/3 单元测试通过；真实 9 图作品包结构与尺寸检查通过。
- **Hypothesis:** 逐页信息增量会减少机械切页；provider-backed comparison 是 `missing evidence`。

## Verification And Limits

- Package validation: PASS，无 failure / warning
- Trigger eval: 15/15，false positive 0，false negative 0
- Validator unit tests: 3/3 PASS
- Real package runtime: 9 张 1080×1440 PNG + `post.md` + contact sheet 通过
- Local discovery: `npx skills add . --list` 发现 5 个 Skills，包含本 Skill
- Isolated copy install: PASS，Skill 入口和全部资源复制完整
- Output eval: specification only; provider-backed evidence missing
- Human blind review: missing evidence
- Remote install: pending PR/default-branch visibility
- Permissions excluded: account login, cookies, tokens, upload and automatic publishing
