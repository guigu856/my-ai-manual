# Social Content Publisher

把已经完成的图文或视频作品安全地发到社交平台，并在提交后回读线上内容，防止“命令成功、作品乱码”。

## 当前范围

- 已验证：小红书静态图文的账号校验、UTF-8 预检、提交、管理页定位、编辑页回读和原笔记修复。
- 已实现并完成提交前页面核验：抖音视频，含标题、正文、标签、横版/竖版封面和发布设置；最终提交后的线上回读证据仍待补齐。
- 已预留：小红书视频、抖音图文、快手图文 / 视频、Bilibili 视频、视频号和 YouTube。
- 预留适配器不会被标记为已支持，只有端到端证据齐全后才升级。

## 安装

```bash
npx skills add guigu856/my-ai-manual --skill social-content-publisher

python C:/Users/<you>/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo guigu856/my-ai-manual \
  --path skills/social-content-publisher
```

## 前提

- Python 3.10+
- 小红书图文与抖音视频：已安装并可调用 `social-auto-upload` 的 `sau`
- 线上自动回读：`patchright` 和可用的 Chromium / Chrome
- 平台账号由本地执行器管理；Cookie、Token 和二维码不进入仓库

## 你可以直接这样说

- “把这 9 张小红书卡片和正文发布到主账号，并检查线上有没有乱码。”
- “把这个视频发到抖音；当前没有适配器就只列出接入缺口。”
- “把这个视频、横版封面和竖版封面发到抖音，先 dry-run 再提交。”
- “刚才发布的标题变成问号了，修复原笔记，不要重复发一条。”
- “先给我 dry-run，核对账号、媒体顺序和发布时间。”

## 快速使用

1. 复制 `templates/publish-manifest.example.json` 到作品目录。
2. 把标题和正文保存为 UTF-8 文件。
3. 预检：

   ```bash
   python scripts/preflight_manifest.py publish-manifest.json
   ```

4. dry-run：

   ```bash
   python scripts/publish_social.py publish-manifest.json
   ```

5. 用户授权后提交：

   ```bash
   python scripts/publish_social.py publish-manifest.json --submit
   ```

6. 回读小红书线上内容：

   ```bash
   python scripts/verify_xiaohongshu_note.py publish-manifest.json
   ```

## 输出

- 预检报告：字符数、CJK 数量、哈希、媒体数量和发布意图 ID
- 发布报告：账号别名、提交状态、平台证据和警告
- 线上核验：标题、正文、编码和媒体数量
- 状态：`published-verified`、`submitted-unverified`、`repair-required` 等

## 风险边界

- 实际发布、修改和删除是外部写操作。
- 同一发布意图已验证成功时，脚本阻断无意重复发布。
- 浏览器网页登录与 CLI 账号文件分别校验。
- 日志退出码为 0 不代表线上正文正确。
- 平台限制会变化，执行前检查当前 CLI 帮助和平台页面。

## Troubleshooting

- **二维码看不到**：复制到稳定路径，并在正式回复中用绝对路径显示。
- **网页已登录但 `sau check` 为 invalid**：完成 `sau` 自己的登录流程。
- **中文变问号**：不要把中文 here-string 管道给 Python；改用 UTF-8 文件和本 Skill 脚本。
- **找不到 Chromium**：先验证本机 Chrome，再按当前上游版本配置浏览器路径。
- **标签被跳过**：发布报告列出失败标签；必要标签同时保留在正文中。

## 验证

```bash
python -m unittest discover -s tests -v
python scripts/preflight_manifest.py templates/publish-manifest.example.json
python C:/Users/<you>/.codex/skills/qiaomu-meta-skill/scripts/validate_skill.py .
```

第二条命令需要先把模板复制到真实作品目录并替换媒体路径。

## 上游参考

当前命令契约参考 `dreammis/social-auto-upload`：<https://github.com/dreammis/social-auto-upload/tree/main/skills>，抖音适配器核验基线为提交 `008e4ff66abdf48eb1f4b999272ef979711af436`。本 Skill 额外增加 UTF-8 门禁、双封面校验、重复发布防护、线上回读和原作品修复。
