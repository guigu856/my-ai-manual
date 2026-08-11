from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from manifest_core import ManifestError, default_report_path, normalize_text, prepare_manifest, resolve_path, write_json


def resolve_match_title(verification: dict[str, object], default_title: str) -> str:
    value = verification.get("match_title")
    if value is None or not str(value).strip():
        return default_title
    return str(value).strip()


async def verify(manifest: str, report_arg: str | None) -> int:
    try:
        prepared = prepare_manifest(manifest)
        verification = prepared.data.get("verification", {})
        if not isinstance(verification, dict):
            raise ManifestError("verification must be an object")
        account_file_value = verification.get("account_file")
        browser_value = verification.get("browser_executable")
        if not isinstance(account_file_value, str) or not isinstance(browser_value, str):
            raise ManifestError("verification.account_file and verification.browser_executable are required")
        account_file = resolve_path(prepared.path, account_file_value)
        browser_executable = resolve_path(prepared.path, browser_value)
        if not account_file.is_file():
            raise ManifestError(f"account file does not exist: {account_file}")
        if not browser_executable.is_file():
            raise ManifestError(f"browser executable does not exist: {browser_executable}")
    except ManifestError as exc:
        print(json.dumps({"status": "verification-failed", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2

    try:
        from patchright.async_api import async_playwright
    except ImportError:
        print(json.dumps({"status": "verification-failed", "error": "patchright is not installed"}, ensure_ascii=False, indent=2))
        return 2

    checks: dict[str, bool] = {}
    platform_id = None
    edit_url = None
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, executable_path=str(browser_executable))
        context = await browser.new_context(storage_state=str(account_file))
        page = await context.new_page()
        await page.goto("https://creator.xiaohongshu.com/new/note-manager", wait_until="domcontentloaded")
        await page.wait_for_timeout(5000)
        match_title = resolve_match_title(verification, prepared.title)
        cards = page.locator(".note-card__body").filter(has_text=match_title)
        card_count = await cards.count()
        candidate_index = verification.get("manager_card_index")
        if card_count == 0:
            await browser.close()
            report = {**prepared.report, "status": "repair-required", "error": "note card not found by title"}
            write_json(Path(report_arg).resolve() if report_arg else default_report_path(prepared), report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 7
        if card_count > 1 and candidate_index is None:
            await browser.close()
            report = {
                **prepared.report,
                "status": "repair-required",
                "error": f"{card_count} note cards match the title; set verification.manager_card_index explicitly",
            }
            write_json(Path(report_arg).resolve() if report_arg else default_report_path(prepared), report)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 7
        index = int(candidate_index or 0)
        if index < 0 or index >= card_count:
            raise RuntimeError(f"verification.manager_card_index out of range: {index}")
        card = cards.nth(index)
        card_title = await card.locator(".note-card__title").inner_text()
        if card_title.strip() != match_title:
            raise RuntimeError(f"manager card title mismatch: {card_title!r}")
        actions = card.locator(".note-card__action-btn")
        if await actions.count() < 3:
            raise RuntimeError("edit action not found")
        await actions.nth(2).click()
        await page.wait_for_timeout(5000)
        edit_url = page.url
        match = re.search(r"[?&]id=([^&]+)", edit_url)
        platform_id = match.group(1) if match else None
        title_input = page.locator('input[placeholder*="填写标题"]').first
        editor = page.locator("[contenteditable='true']").first
        await title_input.wait_for(state="visible", timeout=30000)
        await editor.wait_for(state="visible", timeout=30000)
        online_title = await title_input.input_value()
        online_body = await editor.inner_text()
        page_text = await page.locator("body").inner_text()
        media_match = re.search(r"图片编辑\s*(\d+)\s*/\s*(\d+)", page_text)
        online_media_count = int(media_match.group(1)) if media_match else None
        checks = {
            "title": online_title == prepared.title,
            "body": normalize_text(online_body) == normalize_text(prepared.body),
            "encoding": "\ufffd" not in online_title + online_body and not re.search(r"\?{4,}", online_title + online_body),
            "media_count": online_media_count == len(prepared.media),
        }
        await context.storage_state(path=str(account_file))
        await browser.close()

    status = "published-verified" if all(checks.values()) else "repair-required"
    report_path = Path(report_arg).expanduser().resolve() if report_arg else default_report_path(prepared)
    existing_report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.is_file() else {}
    report = {
        **existing_report,
        **prepared.report,
        "status": status,
        "platform_id": platform_id,
        "platform_url": edit_url,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verification": checks,
        "missing_evidence": [] if status == "published-verified" else [key for key, value in checks.items() if not value],
    }
    write_json(report_path, report)
    print(json.dumps({**report, "report": str(report_path)}, ensure_ascii=False, indent=2))
    return 0 if status == "published-verified" else 7


def main() -> int:
    parser = argparse.ArgumentParser(description="Round-trip verify one Xiaohongshu note.")
    parser.add_argument("manifest")
    parser.add_argument("--report")
    args = parser.parse_args()
    return asyncio.run(verify(args.manifest, args.report))


if __name__ == "__main__":
    raise SystemExit(main())
