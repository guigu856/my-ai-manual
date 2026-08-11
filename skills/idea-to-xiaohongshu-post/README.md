# idea-to-xiaohongshu-post

> 把一个想法真正做成能发布的小红书图文：不只写文案，还交付封面、多页卡图、正文、预览和质检报告。

## 为什么值得用

常见的“小红书文案”只停在标题和正文；常见的“卡片生成器”又容易把长文机械切页。这个 Skill 先锁定观点和证据边界，再重建翻页推进，最后通过浏览器或专用卡片渲染器生成 3:4 PNG，并检查移动端阅读和包结构。

它适合观点、教程、比较、清单、故事和证据型图文。视频成片、账号诊断和自动发布不在范围内。

## 安装

```bash
npx skills add https://github.com/guigu856/my-ai-manual --skill idea-to-xiaohongshu-post
```

验证：

```bash
npx skills add https://github.com/guigu856/my-ai-manual --list
```

## 你可以直接这样说

- “把这个想法做成一套能直接发的小红书图文。”
- “把这篇文章拆成 8 张小红书观点卡，标题正文一起给我。”
- “把这段视频稿改成 3:4 小红书轮播图。”
- “优化这套小红书卡片，修掉断词、空白和逻辑重复。”
- “给这个教程做一套小红书知识卡并生成发布文案。”

## 它会做什么

1. 区分原始材料中的事实、用户观点和推导内容。
2. 判断图文类型，锁定核心观点和适用边界。
3. 生成逐页阅读推进，而不是按字数机械切页。
4. 同时完成卡片文案、标题、正文和话题。
5. 使用专用社交卡 Skill 或 HTML/CSS 浏览器路线渲染 PNG。
6. 生成 contact sheet，检查原尺寸和手机缩略图。
7. 输出 `publish-ready`、`preview-ready` 或 `render-blocked` 状态。

## 前置条件

- [ ] Agent 具备本地文件读写能力。
- [ ] 需要最终 PNG 时，环境具备真实浏览器截图或已安装社交卡渲染 Skill。
- [ ] 使用本包校验脚本时，Python 版本可运行标准库脚本：

```bash
python --version
```

可选渲染适配器：

```bash
npx skills add https://github.com/op7418/guizang-social-card-skill --skill guizang-social-card-skill
```

该适配器使用 AGPL-3.0；安装和复用前自行确认许可证边界。本 Skill 不复制其模板或源代码。

## 输出示例

```text
ai-whetstone-xhs/
├── work-brief.md
├── page-plan.md
├── post.md
├── index.html
├── assets/
├── output/
│   ├── xhs-01.png
│   ├── xhs-02.png
│   └── xhs-09.png
├── preview/contact-sheet.jpg
└── qa-report.md
```

默认卡图为 1080×1440 PNG。精确平台限制会变化；涉及当前上传接口和数量上限时，应重新核对官方来源。

## 包结构检查

在 Skill 目录执行：

```bash
python scripts/validate_xhs_package.py /path/to/task-dir
python -m unittest discover -s tests -p "test_*.py"
```

Skill 包本身的验证命令：

```bash
python /path/to/qiaomu-meta-skill/scripts/validate_skill.py .
```

检查内容包括：

- `post.md` 标题和正文
- `page-plan.md` 与 `qa-report.md`
- 5–18 张连续命名的 PNG
- 每张 1080×1440
- contact sheet
- 重复图片和素材来源提示

确定性脚本只证明文件和图片规格，不替代内容与视觉审查。

## 与相邻 Skills 的边界

| 任务 | 使用 |
|---|---|
| 只写小红书标题和正文，不出图 | `idea-to-platform-content` |
| 从想法到完整静态图文作品包 | `idea-to-xiaohongshu-post` |
| 只做社交卡视觉排版 | `guizang-social-card-skill` 或其它设计 Skill |
| 制作小红书视频成片 | 视频生产 Skill |
| 自动登录和上传发布 | 专用发布器，另行授权 |

## Troubleshooting

| 问题 | 原因 | 解决 |
|---|---|---|
| 只有文案，没有 PNG | 环境缺少渲染器或真实浏览器 | 安装卡片渲染 Skill，或使用 HTML/CSS + Playwright 路线 |
| `P11` 尺寸失败 | 输出不是 1080×1440 | 修正画布尺寸后整组重渲 |
| contact sheet 缺失 | 只导出了单页图片 | 按发布顺序生成 `preview/contact-sheet.jpg` |
| 卡片看着像长文截图 | 没有重建页面职责 | 回到 `page-plan.md`，为每页补唯一信息增量和视觉关系 |
| 标题很吸睛但正文没兑现 | 封面承诺脱离内容 | 修改封面或补足正文机制，保持三者一致 |

## 风险边界

- 网络素材的版权状态需要记录并由发布者判断。
- 图片生成服务可能产生费用；调用前遵守当前工具的确认规则。
- Skill 不读取或保存小红书账号 Cookie、Token 和密码。
- Skill 不自动发布，也不承诺流量、收藏、转化或涨粉结果。

## 致谢

- [idea-to-platform-content](https://github.com/guigu856/my-ai-manual/tree/main/skills/idea-to-platform-content)：来源忠实、平台/形态分离和文稿交付边界。
- [guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)：3:4 卡片系统、HTML 渲染、移动端检查和 DOM 级验证思路。
- [xhs-markdown-card-collab](https://github.com/Sven-LI-sankyuu/presentation-skills/tree/main/xhs-markdown-card-collab)：Markdown 清理、分页、真实浏览器导出和移动端阅读检查。
- [xhs-writer-skill](https://github.com/JuneYaooo/xhs-writer-skill)：完整发布包、真实素材优先和标题/正文/卡片一起交付。

## License

本目录暂未单独声明许可证，沿用仓库未来的根级许可证决策。在明确许可证前，不把本目录内容描述为可自由再分发。
