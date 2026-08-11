# 发布前质量门禁

## 状态定义

| 状态 | 含义 |
|---|---|
| `draft` | 只有内容或页面计划 |
| `render-blocked` | 文稿齐全，但渲染能力或依赖缺失 |
| `preview-ready` | 已有卡图和预览，仍有待确认或待修问题 |
| `publish-ready` | 内容、视觉、移动端和技术检查通过 |

## Gate A：来源与观点

- 核心观点来自用户材料或已标注的外部来源。
- 主语、对象、因果和边界没有被改写。
- 已确认事实、用户判断和推导内容可以区分。
- 新闻、政策、产品参数、平台规则和统计数字有当前来源。
- 没有编造案例、评价、体验、数据和人群共识。

## Gate B：卡片叙事

- 封面承诺在正文中被解释。
- 每页有唯一主要职责。
- 每页相对上一页有信息增量。
- 机制、证据和边界没有被口号替代。
- 结尾互动承接正文中的真实分歧。
- 标题、卡图、`post.md` 的结论一致。

## Gate C：视觉表达

- 视觉结构与语义一致：比较、流程、层级、警示、证据等关系没有错配。
- 没有无意义数字、装饰图表、随机图标和无关 AI 素材。
- 一组作品只有一个视觉系统和一个主锚点色。
- 页面之间有变化，但标题、正文、页码和页脚锚点稳定。
- 图片主体没有被裁掉；截图关键文字仍可读。

## Gate D：排版与移动端阅读

- 原始尺寸下没有溢出、截断、重叠和页脚碰撞。
- 没有孤行、单字掉行和语义断裂换行。
- 360px 宽缩略图下封面和正文仍能阅读。
- 卡片下部没有未经设计的大面积空白。
- 连续页面没有机械重复同一版式。
- 中文标点、引号、大小写和空格风格一致。

## Gate E：技术包

- `post.md` 包含非空标题和正文。
- `page-plan.md` 存在。
- `output/` 内有 5–18 张按顺序命名的 PNG。
- 每张 PNG 为 1080×1440。
- 没有完全重复的输出图片。
- contact sheet 存在并按发布顺序排列。
- `qa-report.md` 存在并记录检查结论。
- 素材来源记录存在；未使用外部素材时注明“无外部素材”。

运行：

```bash
python scripts/validate_xhs_package.py <task-dir>
```

确定性检查通过只证明包结构和图片规格，不证明观点正确或视觉优秀。内容和视觉仍需按 Gate A–D 检查。

## QA 报告格式

```markdown
# QA Report

- Status: publish-ready | preview-ready | render-blocked
- Checked at: YYYY-MM-DD
- Card count: N
- Size: 1080×1440

## Source fidelity
- PASS/FAIL — 说明

## Story and copy
- PASS/FAIL — 说明

## Visual and mobile readability
- PASS/FAIL — 说明

## Technical package
- PASS/FAIL — 命令和结果

## Unresolved issues
- 无
```

有未解决问题时逐条写页码、问题、严重级和源文件修复动作。
