---
name: social-content-publisher
description: 自动发布已经准备好的社交媒体作品包：检查媒体、封面、标题、正文、账号与发布时间，完成登录或 Cookie 校验，选择平台与作品形态适配器，提交发布，并回读线上内容确认没有乱码、截断或错发。Use whenever the user asks to 发布、上传、定时发布、批量分发、保存草稿、检查登录状态、修复已发布乱码，或把成品发到小红书、抖音、快手、Bilibili、视频号、YouTube 等平台。当前已端到端验证小红书静态图文；抖音视频已实现 CLI 适配器并完成提交前页面核验，但尚缺最终提交后的线上回读证据；其他作品形态按适配器契约扩展。不用于内容创作、卡图制作、视频剪辑、账号运营分析或只写文案。
metadata:
  version: "0.2.0"
  owner: guigu856
---

# 社交内容自动发布

## 作用定位

接收已经完成的作品包，负责从本地成品到平台线上成品的最后一公里：

```text
作品包
→ 适配器选择
→ 账号校验
→ UTF-8 与媒体预检
→ 发布授权
→ 提交
→ 线上回读核验
→ 修复或交付发布凭据
```

本 Skill 不把“命令返回成功”当作“内容发布正确”。只有平台提交成功且线上标题、正文、媒体数量通过回读，状态才是 `published-verified`。

## 当前能力

| 平台 | 作品形态 | 状态 | 执行入口 |
|---|---|---|---|
| 小红书 | 静态图文 | `validated` | `scripts/publish_social.py` |
| 小红书 | 视频 | `reserved` | 适配器位置已预留 |
| 抖音 | 视频 | `pre-submit-validated` | `scripts/publish_social.py` |
| 抖音 | 图文 | `reserved` | 适配器位置已预留 |
| 快手 | 图文 / 视频 | `reserved` | 适配器位置已预留 |
| Bilibili | 视频 | `reserved` | 适配器位置已预留 |
| 视频号 | 图文 / 视频 | `reserved` | 适配器位置已预留 |
| YouTube | 视频 | `reserved` | 适配器位置已预留 |

`reserved` 表示结构和契约已定义，但没有本地端到端发布证据。读取 `references/platform-adapters.md` 查看支持矩阵与扩展方法。

## 状态机

```text
package-ready
→ authenticated
→ preflight-passed
→ submit-authorized
→ submitted
→ published-verified
```

失败状态：

- `auth-required`：登录信息缺失或失效。
- `preflight-failed`：媒体、元数据、编码或平台约束未通过。
- `submitted-unverified`：平台已接收，但没有完成线上回读。
- `repair-required`：线上内容与本地作品包不一致。

## 核心工作流

### Gate 1：锁定发布意图

从上下文确定：

- 平台和作品形态
- 账号别名，不读取或展示 Cookie、Token、密码
- 立即发布、定时发布或保存草稿
- 媒体、标题、正文、标签和封面来源
- 是否允许公开提交

用户已经明确说“发布到某平台”且作品包唯一时，直接执行，不重复确认。平台、账号、发布时间或作品包存在多个候选且会导致错发时，先确认该歧义。

提交是外部写操作。首次提交前必须能回答：发布到哪个平台、哪个账号、哪套作品、何时发布。删除、覆盖和重发属于新的写操作，按 `references/security-and-side-effects.md` 执行。

### Gate 2：创建发布清单

从 `templates/publish-manifest.example.json` 复制清单，在任务目录填写相对路径。标题和正文放在 UTF-8 文件中，不把长中文直接塞进 PowerShell 管道。

至少包含：

```text
platform / content_type / account
title_file / body_file / media
tags / covers / schedule / browser_mode
verification / runtime
```

平台与作品形态缺少适配器时，输出 `adapter-reserved`，列出缺失字段和验证任务，不伪装成已支持。

### Gate 3：账号与运行环境预检

1. 查找平台专用 CLI、连接器或 API；当前小红书图文与抖音视频优先使用已安装的 `sau`。
2. 执行账号校验，例如：

   ```bash
   sau xiaohongshu check --account <account>
   sau douyin check --account <account>
   ```

3. 登录失效时执行登录流程。二维码必须直接显示给用户；若上游会删除临时二维码，先复制到稳定路径，再在正式回复中显示，并标注生成时间和有效期。
4. 登录成功后再次运行 `check`，不能只依据用户说“已登录”或浏览器主页可见来推断 CLI 账号文件有效。
5. 检查浏览器运行时。若自动化依赖的 Chromium 缺失，先验证已安装 Chrome 是否可用，再按当前依赖版本处理，不能在发布时临时猜路径。

### Gate 4：确定性预检

运行：

```bash
python scripts/preflight_manifest.py <publish-manifest.json> --json-out <preflight-report.json>
```

阻断条件：

- 标题、正文或清单不是严格 UTF-8。
- 中文作品的标题或正文没有 CJK 字符，却出现连续 `????`。
- 媒体缺失、重复、不可读或扩展名不符合适配器。
- 抖音视频不是单个可识别视频，或显式横版/竖版封面不是有效 PNG/JPEG。
- 标题会被当前适配器静默截断。
- 已存在同一 `publish_intent_id` 的 `published-verified` 报告，用户又没有明确要求重发。
- 清单包含 Cookie、Token、密码或私钥。

预检报告记录字符数、CJK 数量、SHA-256、媒体数量和发布意图 ID；不记录秘密。

### Gate 5：构建命令但先不提交

先运行 dry-run：

```bash
python scripts/publish_social.py <publish-manifest.json>
```

检查输出中的适配器、账号别名、媒体数量和顺序、标题 / 正文字符数与哈希、立即或定时发布以及即将调用的执行器。命令预览不得输出 Cookie 或正文全文。

### Gate 6：提交

用户已授权后运行：

```bash
python scripts/publish_social.py <publish-manifest.json> --submit
```

小红书图文和抖音视频适配器使用 Python `subprocess` 参数列表调用 `sau`，不经过 PowerShell 文本管道。抖音视频映射 `title + desc + tags`，并可分别传递横版、竖版封面。平台返回成功后，状态先写为 `submitted`，等待 Gate 7。

### Gate 7：线上回读核验

核验至少包含：

- 线上标题与本地标题一致
- 正文关键段和末尾一致
- 没有 Unicode 替换字符或连续问号乱码
- 媒体数量与顺序一致
- 发布时间 / 可见性与请求一致

小红书静态图文读取 `references/xiaohongshu-note.md`，抖音视频读取 `references/douyin-video.md`。CLI 的成功标记只证明提交成功，不证明中文内容、封面和可见性正确。

通过后写 `published-verified` 报告。核验条件不足时写 `submitted-unverified`，明确缺少哪项证据。

### Gate 8：修复

线上内容不一致时：

1. 保留媒体和原笔记 ID，优先编辑原笔记，避免重复发布。
2. 从 UTF-8 文件重新填充标题和正文。
3. 提交前在页面内回读输入值，比较字符数、哈希和关键片段。
4. 更新后重新进入编辑页验证，不沿用旧的成功日志。
5. 只有用户明确要求删除或重复发布时，才删除或创建第二条作品。

小红书修复命令见 `references/failure-recovery.md`。

## 交付契约

发布完成时给出：

- 平台、账号别名、作品形态
- 实际标题、媒体数量、发布时间
- 发布状态：`published-verified` / `submitted-unverified` / 失败状态
- 平台返回的作品 URL、作品 ID 或成功页证据（若可获得）
- 线上回读通过项和缺失证据
- 被平台跳过的标签、封面或其它字段
- 发布报告绝对路径

不把终端退出码为 0 单独写成“发布正确”。

## 路由与边界

- 成品尚未制作：先调用内容、图文或视频生产 Skill，本 Skill 只接收完成包。
- 只需小红书图文作品包：交给 `idea-to-xiaohongshu-post`；完成后再回到本 Skill。
- 只需文案：交给 `idea-to-platform-content`。
- 账号运营、选题和数据分析不属于发布执行。
- 平台规则、标题限制和媒体上限会变化；执行前以当前 CLI 帮助和平台页面为准。

## Reference Map

| 需要 | 文件 |
|---|---|
| 完整状态机、门禁和幂等策略 | `references/workflow-and-gates.md` |
| 小红书图文执行与回读 | `references/xiaohongshu-note.md` |
| 抖音视频执行、浏览器接管与证据边界 | `references/douyin-video.md` |
| 其它平台 / 作品形态预留 | `references/platform-adapters.md` |
| 新适配器接口 | `references/adapter-contract.md` |
| 登录、乱码、浏览器和重复发布修复 | `references/failure-recovery.md` |
| 秘密、权限和外部写操作 | `references/security-and-side-effects.md` |

## 失效规则

- 不把浏览器网页登录与 CLI 账号文件混为一谈。
- 不把二维码只放在隐藏工具输出或即将删除的临时路径中。
- 不通过 PowerShell 管道传递中文标题和正文。
- 不把平台成功页当作内容一致性证据。
- 不因核验失败自动重复发布。
- 不把 `reserved` 适配器写成“支持”。
- 不提交 Cookie、Token、密码、二维码、账号文件或含秘密的运行日志。
