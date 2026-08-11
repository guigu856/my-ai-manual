# 适配器契约

## 输入

适配器接收已经通过通用预检的标准对象：

```text
platform
content_type
account
title
body
ordered media paths
tags
thumbnail
schedule
visibility
platform_options
runtime
verification
publish_intent_id
```

## 必须实现

每个适配器必须提供：

1. `capabilities()`：支持的平台、形态、字段和已验证范围。
2. `validate()`：平台必填字段、媒体规则、标题规则和调度规则。
3. `check_auth()`：返回明确的账号状态，不读取或打印秘密。
4. `build_dry_run()`：输出脱敏的执行摘要。
5. `submit()`：执行一次写操作，返回平台证据。
6. `verify()`：从线上回读标题、正文、媒体和可见性。
7. `repair()`：在同一作品 ID 上纠正内容，或明确标记不支持。
8. `rollback_boundary()`：说明删除、撤回和重复发布需要的授权。

## 结果

```json
{
  "status": "submitted | submitted-unverified | published-verified | repair-required",
  "platform_id": null,
  "platform_url": null,
  "submitted_at": null,
  "verified_at": null,
  "checks": {},
  "warnings": [],
  "missing_evidence": []
}
```

## 适配器升级门禁

只有真实端到端夹具通过，才能把适配器从 `reserved` 改为 `validated`。CLI 帮助存在、代码看起来支持、成功页出现或 dry-run 通过，单独都不是端到端证据。
