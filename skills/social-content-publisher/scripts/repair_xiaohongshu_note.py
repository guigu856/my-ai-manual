from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from manifest_core import ManifestError, default_report_path, normalize_text, prepare_manifest, resolve_path, write_json


async def repair(manifest: str, edit_url: str, submit: bool, report_arg: str | None) -> int:
    try:
        prepared = prepare_manifest(manifest)
        verification = prepared.data.get("verification", {})
        if not isinstance(verification, dict):
            raise ManifestError("verification must be an object")
        account_file_value = verification["account_file"]
        browser_value = verification["browser_executable"]
        if not isinstance(account_file_value, str) or not account_file_value.strip():
            raise ManifestError("verification.account_file must be a path string")
        if not isinstance(browser_value, str) or not browser_value.strip():
            raise ManifestError("verification.browser_executable must be a path string")
        account_file = resolve_path(prepared.path, account_file_value)
        browser_executable = resolve_path(prepared.path, browser_value)
        if not account_file.is_file():
            raise ManifestError(f"account file does not exist: {account_file}")
        if not browser_executable.is_file():
            raise ManifestError(f"browser executable does not exist: {browser_executable}")
    except (ManifestError, KeyError) as exc:
        print(json.dumps({"status": "repair-failed", "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2
    if not submit:
        print(json.dumps({**prepared.report, "status": "repair-dry-run", "edit_url": edit_url}, ensure_ascii=False, indent=2))
        return 0

    try:
        from patchright.async_api import async_playwright
    except ImportError:
        print(json.dumps({"status": "repair-failed", "error": "patchright is not installed"}, ensure_ascii=False, indent=2))
        return 2

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True, executable_path=str(browser_executable))
        context = await browser.new_context(storage_state=str(account_file))
        page = await context.new_page()
        await page.goto(edit_url, wait_until="domcontentloaded")
        title_input = page.locator('input[placeholder*="填写标题"]').first
        editor = page.locator("[contenteditable='true']").first
        await title_input.wait_for(state="visible", timeout=30000)
        await editor.wait_for(state="visible", timeout=30000)
        await title_input.fill(prepared.title)
        await editor.click()
        await page.keyboard.press("Control+A")
        await page.keyboard.press("Backspace")
        await page.keyboard.insert_text(prepared.body)
        pre_title = await title_input.input_value()
        pre_body = await editor.inner_text()
        if pre_title != prepared.title or normalize_text(pre_body) != normalize_text(prepared.body):
            raise RuntimeError("pre-submit editor round-trip mismatch")
        if "\ufffd" in pre_title + pre_body or re.search(r"\?{4,}", pre_title + pre_body):
            raise RuntimeError("pre-submit encoding corruption detected")
        await page.keyboard.press("Escape")
        await title_input.click()
        await page.get_by_role("button", name="发布", exact=True).click(force=True)
        await page.wait_for_timeout(6000)
        success_url = page.url
        if "editSuccess" not in success_url and "publish/success" not in success_url:
            raise RuntimeError(f"unexpected post-update URL: {success_url}")

        await page.goto(edit_url, wait_until="domcontentloaded")
        await title_input.wait_for(state="visible", timeout=30000)
        await editor.wait_for(state="visible", timeout=30000)
        final_title = await title_input.input_value()
        final_body = await editor.inner_text()
        page_text = await page.locator("body").inner_text()
        media_match = re.search(r"图片编辑\s*(\d+)\s*/\s*(\d+)", page_text)
        online_media_count = int(media_match.group(1)) if media_match else None
        checks = {
            "title": final_title == prepared.title,
            "body": normalize_text(final_body) == normalize_text(prepared.body),
            "encoding": "\ufffd" not in final_title + final_body and not re.search(r"\?{4,}", final_title + final_body),
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
        "platform_url": edit_url,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "verification": checks,
        "repair": {"success_url": success_url},
    }
    write_json(report_path, report)
    print(json.dumps({**report, "report": str(report_path)}, ensure_ascii=False, indent=2))
    return 0 if status == "published-verified" else 7


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair one existing Xiaohongshu note with UTF-8 files.")
    parser.add_argument("manifest")
    parser.add_argument("--edit-url", required=True)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--report")
    args = parser.parse_args()
    return asyncio.run(repair(args.manifest, args.edit_url, args.submit, args.report))


if __name__ == "__main__":
    raise SystemExit(main())
