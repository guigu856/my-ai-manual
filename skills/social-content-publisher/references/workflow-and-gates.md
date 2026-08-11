# 发布状态机与门禁

## 1. 状态

| 状态 | 含义 | 可否声称发布完成 |
|---|---|---|
| `package-ready` | 媒体与文案已准备 | 否 |
| `authenticated` | 执行器账号校验通过 | 否 |
| `preflight-passed` | 编码、媒体和平台字段通过 | 否 |
| `submit-authorized` | 用户已授权该平台、账号和时间的写操作 | 否 |
| `submitted` | 平台接受提交或进入成功页 | 否 |
| `submitted-unverified` | 已提交，但线上内容尚未回读 | 否 |
| `published-verified` | 线上标题、正文和媒体通过核验 | 是 |
| `repair-required` | 线上内容存在乱码、截断、错发或缺项 | 否 |

## 2. 发布意图 ID

用以下字段生成稳定 ID：

```text
platform
content_type
account alias
title SHA-256
body SHA-256
ordered media SHA-256 list
schedule
visibility
```

同一意图已经存在 `published-verified` 报告时，默认阻断再次提交。用户明确要求重发时生成新的 `retry_of` 关系，不能覆盖旧报告。

## 3. 写操作边界

- “发布这套作品到小红书主账号”已经授权一次明确发布，不再重复询问。
- “帮我发一下”但存在多个账号或多个作品包时，先确认会改变目标的歧义。
- 修改原笔记用于纠正本次错误，可以沿用修复意图；删除、换账号、改可见性、改定时时间或重复发布需要新的明确授权。
- 保存草稿和公开发布是不同操作，不互相替代。

## 4. 门禁顺序

1. **目标门禁**：平台、形态、账号、时间、作品包唯一。
2. **依赖门禁**：执行器、浏览器、账号状态可用。
3. **编码门禁**：严格 UTF-8、CJK 存在、无连续问号和替换字符。
4. **媒体门禁**：文件存在、顺序稳定、无重复、规格满足适配器。
5. **字段门禁**：标题、正文、标签、分类、封面等必填项齐全。
6. **幂等门禁**：无已验证的相同发布意图。
7. **授权门禁**：外部写操作范围与用户请求一致。
8. **提交门禁**：先 dry-run，再执行。
9. **线上门禁**：管理页 / 编辑页回读与本地哈希和关键片段一致。

## 5. 报告字段

每次执行写一个不含秘密的 JSON 报告：

```json
{
  "publish_intent_id": "sha256:...",
  "platform": "xiaohongshu",
  "content_type": "note",
  "account": "main",
  "status": "published-verified",
  "title_sha256": "...",
  "body_sha256": "...",
  "media_count": 9,
  "platform_id": "...",
  "platform_url": "...",
  "submitted_at": "...",
  "verified_at": "...",
  "verification": {
    "title": true,
    "body_fragments": true,
    "encoding": true,
    "media_count": true
  },
  "warnings": []
}
```

平台没有返回作品 ID 或 URL 时保留空值，并把证据写成 `missing evidence`。
