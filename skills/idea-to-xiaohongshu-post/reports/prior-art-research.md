# Prior-Art Research

- Researched at: 2026-08-11
- Queries: `xiaohongshu carousel social cards`; `idea to rednote post`
- Catalogs: skills.sh、SkillsMP、GitHub canonical source
- Rating evidence: unavailable
- Unified runner: Windows 下未解析无扩展名 `npx`；改用 `npx.cmd` 和 SkillsMP 客户端分别完成查询

| Candidate | Relevance | skills.sh installs | GitHub stars | Quality / trust evidence | Adopt | Reject | License |
|---|---|---:|---:|---|---|---|---|
| `idea-to-platform-content` | 上游内容契约 | — | — | 当前仓库既有 Skill，已检查 `SKILL.md` 和小红书/图文路由 | 来源忠实、平台与形态分离、去 AI 味 | 只交付文稿，不承担视觉成品 | 仓库根许可证未声明 |
| `guizang-social-card-skill` | 视觉生产 | 4.2K | 6.2K | 真实 `SKILL.md`、种子模板、版式 references 和 DOM validator 已检查 | 3:4、HTML→PNG、contact sheet、移动端和 DOM 检查 | 不复制模板和源代码；不继承“先展示再验证”作为发布就绪门禁 | AGPL-3.0 |
| `xhs-markdown-card-collab` | 浏览器卡片 | missing evidence | 164 | GitHub README 公开实际 demo 和检查项 | Markdown 清理、分页、真实浏览器导出、孤行/空白检查 | 不采用协作审批作为默认前置；当前 Skill上下文足够时直接执行 | 需在代码复用前核对 |
| `xhs-writer-skill` | 完整发布包 | missing evidence | 123 | GitHub README、输出结构和 Apache-2.0 已核对 | 真实素材优先、卡片 + caption + hashtags 一起交付 | 不采用“爆款公式”、固定素人 emoji 风和默认搜索对标爆款 | Apache-2.0 |

> skills.sh installs 是安装量，不是评分；GitHub stars 是仓库关注度，不证明输出质量。以上数值为 2026-08-11 观察值。

## Keep / Adapt / Reject / Invent

### Keep

- 保留 `idea-to-platform-content` 的来源忠实、平台/形态分离和事实边界。
- 保留 `guizang-social-card-skill` 的 3:4 浏览器渲染、功能性版式和移动端检查。
- 保留 `xhs-markdown-card-collab` 的分页、孤行、空白和真实浏览器导出检查。
- 保留 `xhs-writer-skill` 的完整作品包，而不是只给标题和正文。

### Adapt

- 把“素材优先”改成按内容关系选择；抽象观点允许功能性排版，不强制图片。
- 把视觉 validator 作为一个检查层，外加来源忠实、页面推进和标题/卡图/正文一致性门禁。
- 把平台规格标为默认生产参数；用户要求当前规则时再核对官方来源。

### Reject

- 不默认追逐爆款标题、热点词和身份共鸣公式。
- 不把 AI 生图作为整个卡片组的默认渲染方式。
- 不复制 AGPL 上游模板或长段说明。
- 不在同一 Skill内加入账号登录、上传和自动发布。

### Invent

- `work-brief.md` 锁定主语、对象、因果、事实和推导边界。
- `page-plan.md` 为每页记录唯一职责和信息增量。
- `publish-ready / preview-ready / render-blocked` 三态交付，阻止把预览冒充成片。
- 标题、卡图和正文的承诺一致性门禁。
- 标准库 `validate_xhs_package.py`，不依赖 Pillow 即可检查 PNG 尺寸和发布包结构。

## Created Skill Advantages

- **Design advantage:** 将内容忠实、翻页叙事、视觉渲染和发布包检查放在同一输出契约内。
- **Validated advantage:** `validate_xhs_package.py` 的有效包、错误尺寸和缺失文案三类单元测试通过后才可标记脚本已验证。
- **Hypothesis:** 逐页信息增量和三态交付预计会减少“长文机械切页”和“预览即成品”，但 provider-backed 对照和真实发布数据是 `missing evidence`。

## Missing Evidence

- 没有公开用户评分字段。
- 没有 provider-backed 多主题输出对照。
- 没有盲评或真实小红书发布数据。
- 新 Skill 合并后的远程安装证明需在 PR / 默认分支可见后执行。
