# 抖音视频适配器

## 能力状态

`douyin/video` 已实现 `sau` 命令映射，并在 2026-08-12 使用真实已登录的抖音创作者中心完成上传、标题/正文回读、横竖封面配置和封面检测。实际“发布”按钮未点击，线上作品列表也未回读，因此状态是 `pre-submit-validated`，不是 `published-verified`。

上游核验基线：`dreammis/social-auto-upload@008e4ff66abdf48eb1f4b999272ef979711af436`。

## 清单字段

```json
{
  "platform": "douyin",
  "content_type": "video",
  "account": "main",
  "title_file": "content/title.txt",
  "body_file": "content/body.md",
  "media": ["output/video.mp4"],
  "covers": {
    "landscape": "output/cover-landscape.jpg",
    "portrait": "output/cover-portrait.jpg"
  },
  "tags": ["AI", "人工智能"],
  "schedule": null,
  "browser_mode": "headed"
}
```

约束：

- 恰好一个视频；当前校验 MP4、MOV、M4V、WebM、AVI 的扩展名和文件签名。
- 标题按实测页面上限 30 字符预检，正文按 1000 字符预检；平台规则可能变化，执行前复核当前页面与 CLI 帮助。
- `covers.landscape` 和 `covers.portrait` 都是可选字段；缺少任一项会产生警告，因为平台可能自动裁切。
- 封面使用 PNG/JPEG，并校验文件签名。
- 标签通过逗号连接后传给 `--tags`。

## CLI 主路径

```bash
sau douyin check --account main
sau douyin upload-video \
  --account main \
  --file output/video.mp4 \
  --title "<UTF-8 标题>" \
  --desc "<UTF-8 正文>" \
  --tags "AI,人工智能" \
  --thumbnail-landscape output/cover-landscape.jpg \
  --thumbnail-portrait output/cover-portrait.jpg \
  --headed
```

正式执行应通过 `scripts/publish_social.py` 构造参数列表，避免 shell 文本管道改写中文。

## 已登录浏览器接管路径

CLI 账号校验失效、二维码频繁过期，而 Edge 已保留登录态时，可接管已登录的抖音创作者中心：

1. 确认浏览器控制扩展已连接。
2. 若文件选择被浏览器拒绝，在 Edge 扩展详情中开启“允许访问文件 URL”。权限切换会短暂重载扩展，等待重连后重新获取标签页。
3. 上传唯一视频，等待页面完成转码并出现编辑表单。
4. 填入标题、正文和标签，并从页面回读字符计数与实际文本。
5. 分别设置横版和竖版封面；若页面把横版封面自动同步到竖版，明确记录这是自动裁切，不冒充独立竖版资产。
6. 回读封面检测、可见性、立即/定时发布设置。
7. 点击发布后进入作品管理页，按本地标题、时间和媒体特征定位新作品；旧的同名作品不能作为本次证据。

## 证据门禁

页面显示“封面检测通过”只证明提交前配置通过。只有发布后回读到本次新作品的标题、正文、视频、横竖封面、可见性和时间，才写 `published-verified`。页面自动合并或改写标签时，把实际线上值和差异写入报告。

## 已观察故障

- 自动化二维码生成后约十余秒即显示过期，导出的二维码截图不稳定；优先复用真实浏览器登录态。
- CLI 的登录文件与网页登录态是两套状态，分别校验。
- 浏览器文件上传被拒绝时，先检查扩展的文件 URL 权限，再重新连接浏览器。
- 页面可能把正文末尾的标签展示为另一种合并形式，最终以线上回读为准。
