# 小红书静态图文适配器

## 已验证边界

- 执行器：`social-auto-upload` 的 `sau xiaohongshu` CLI。
- 作品形态：多张 PNG/JPEG + 标题 + 正文 + 标签。
- 验证记录：2026-08-11 使用 9 张 1080×1440 PNG 完成登录、提交、管理页定位、原笔记编辑修复和编辑页回读。
- 当前上游版本证据：`dreammis/social-auto-upload` `main@008e4ff66abdf48eb1f4b999272ef979711af436`。
- 平台规则会变化；执行时重新查看 `sau xiaohongshu --help` 和平台页面。

## 命令契约

```bash
sau xiaohongshu login --account <account> [--headless | --headed]
sau xiaohongshu check --account <account>
sau xiaohongshu upload-note \
  --account <account> \
  --images <image-1> [image-2 ...] \
  --title <title> \
  --note <body> \
  [--tags tag1,tag2] \
  [--schedule "YYYY-MM-DD HH:MM"] \
  [--headless | --headed]
```

不要在 PowerShell 中把含中文的 here-string 管道给 Python 再调用 CLI。使用 UTF-8 文件 + `scripts/publish_social.py`，让 Python 以参数列表调用子进程。

## 登录

1. 运行 `check`。输出必须明确包含 `valid`。
2. 失效时运行 `login`。
3. 登录流程生成二维码后，把图片复制到任务目录的稳定路径；正式回复使用绝对路径显示图片。
4. 用户扫码确认后等待登录进程退出码 0，并再次运行 `check`。
5. 浏览器创作中心已登录，不等于 `sau` 的账号文件已生成。

## 预检

- 标题长度不得超过当前适配器的 20 字符安全值，避免上游静默 `[:20]` 截断。
- 媒体必须按发布顺序写入清单；重复路径阻断。
- 中文标题和正文必须含 CJK 字符，出现四个以上连续问号时阻断。
- 标签候选可能在平台 UI 中匹配失败；日志必须保留被跳过的标签。

## 提交

先执行：

```bash
python scripts/publish_social.py publish-manifest.json
```

确认 dry-run 后：

```bash
python scripts/publish_social.py publish-manifest.json --submit
```

看到 `publish/success` 或上游“提交成功”后，状态仅为 `submitted`。

## 线上回读

优先使用清单中的 `verification.account_file` 和 `verification.browser_executable`：

```bash
python scripts/verify_xiaohongshu_note.py publish-manifest.json
```

验证器进入笔记管理页，用标题定位卡片，再进入编辑页读取。存在多个同名作品时默认阻断，并要求在清单中显式填写 `verification.manager_card_index`，避免回读错误作品：

- 标题输入值
- 正文 `contenteditable` 文本
- 媒体计数文本
- 问号乱码与 Unicode 替换字符

全部通过才写 `published-verified`。

## 修复

线上文本损坏时优先编辑原笔记：

```bash
python scripts/repair_xiaohongshu_note.py publish-manifest.json --edit-url <platform-edit-url> --submit
```

修复器在点击发布前先读取页面输入值，与本地标题和正文比较；更新成功后重新进入编辑页核验。不要因乱码直接重复发布。
