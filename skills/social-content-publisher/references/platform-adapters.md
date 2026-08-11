# 平台与作品形态适配器

## 支持矩阵

| 平台 | `platform` | `content_type` | 上游命令契约 | 本 Skill 状态 |
|---|---|---|---|---|
| 小红书图文 | `xiaohongshu` | `note` | `sau xiaohongshu upload-note` | `validated` |
| 小红书视频 | `xiaohongshu` | `video` | `sau xiaohongshu upload-video` | `reserved` |
| 抖音图文 | `douyin` | `note` | `sau douyin upload-note` | `reserved` |
| 抖音视频 | `douyin` | `video` | `sau douyin upload-video` | `pre-submit-validated` |
| 快手图文 | `kuaishou` | `note` | `sau kuaishou upload-note` | `reserved` |
| 快手视频 | `kuaishou` | `video` | `sau kuaishou upload-video` | `reserved` |
| Bilibili 视频 | `bilibili` | `video` | `sau bilibili upload-video` | `reserved` |
| 视频号图文 | `tencent` | `note` | 待核验 | `reserved` |
| 视频号视频 | `tencent` | `video` | 待核验 | `reserved` |
| YouTube 视频 | `youtube` | `video` | 待核验 | `reserved` |

`reserved` 只表示目录、清单字段和状态机已经能容纳该适配器。新增真实支持前必须完成：

1. 当前 CLI / API 帮助核验。
2. 登录和账号校验。
3. 最小媒体包提交。
4. 平台成功页或作品 ID 证据。
5. 线上标题、正文、媒体与可见性回读。
6. 失败恢复和重复发布测试。
7. 更新本表为 `validated` 并记录日期、版本和范围。

## 预留目录

```text
references/platforms/
├── xiaohongshu-note.md       # 当前实现由上级 reference 承载
├── xiaohongshu-video.md      # reserved
├── douyin-note.md            # reserved
├── douyin-video.md           # implemented, pre-submit-validated
├── kuaishou-note.md          # reserved
├── kuaishou-video.md         # reserved
├── bilibili-video.md         # reserved
├── tencent-note.md           # reserved
├── tencent-video.md          # reserved
└── youtube-video.md          # reserved
```

不为 `reserved` 适配器创建空文件。实现时再创建对应 reference、脚本与 eval，避免空壳目录冒充能力。

## 当前已研究的上游 Skill

- `xiaohongshu-upload`：保留 `login → check → upload` 命令主线；补上线上回读与乱码恢复。
- `douyin-upload`：视频采用 `title + desc + tags`，并支持横版/竖版封面；已完成真实登录态下的上传、表单回读和封面检测，最终点击发布及线上成品回读证据尚待补齐。核验基线：`dreammis/social-auto-upload@008e4ff66abdf48eb1f4b999272ef979711af436`。
- `kuaishou-upload`：借鉴图文多图片真实性约束；本地发布证据缺失。
- `bilibili-upload`：借鉴分类 `tid` 必填和真实终端登录边界；本地发布证据缺失。
