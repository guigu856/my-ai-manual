from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import urlparse

from _common import SkillError, command, emit, fail, run, sha256_file, write_json


URL_PATTERN = re.compile(r"https?://[^\s<>\]\[\"']+")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="固化本地视频、链接或平台分享文本。")
    parser.add_argument("source", help="本地视频路径、URL 或包含 URL 的分享文本")
    parser.add_argument("--output-dir", required=True, type=Path, help="本次任务输出目录")
    parser.add_argument("--cookies", type=Path, help="yt-dlp 使用的 Netscape Cookie 文件")
    parser.add_argument("--proxy", help="下载使用的 HTTP(S) 代理")
    return parser


def looks_like_local_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", value)) or value.startswith(("/", "./", "../"))


def unique_destination(directory: Path, name: str) -> Path:
    candidate = directory / name
    if not candidate.exists():
        return candidate
    stem, suffix = candidate.stem, candidate.suffix
    index = 2
    while True:
        candidate = directory / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def local_source(source: Path, original_input: str, output_dir: Path) -> dict[str, object]:
    if not source.is_file():
        raise SkillError(
            "local_source_missing",
            "指定的本地视频文件不存在。",
            {"source": str(source)},
        )
    source_dir = output_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    destination = unique_destination(source_dir, source.name)
    shutil.copy2(source, destination)
    resolved = destination.resolve()
    return {
        "source_kind": "local_file",
        "original_input": original_input,
        "resolved_url": None,
        "platform": "local",
        "local_path": str(resolved),
        "file_name": resolved.name,
        "size_bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def platform_name(url: str) -> str:
    host = (urlparse(url).hostname or "web").lower()
    known = {
        "douyin.com": "Douyin",
        "tiktok.com": "TikTok",
        "youtube.com": "YouTube",
        "youtu.be": "YouTube",
        "bilibili.com": "Bilibili",
        "xiaohongshu.com": "Xiaohongshu",
    }
    for domain, name in known.items():
        if host == domain or host.endswith("." + domain):
            return name
    return host


def downloaded_source(
    original_input: str,
    url: str,
    output_dir: Path,
    cookies: Path | None,
    proxy: str | None,
) -> dict[str, object]:
    source_dir = output_dir / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    args = [
        command("yt-dlp"),
        "--no-playlist",
        "--windows-filenames",
        "--print",
        "after_move:filepath",
        "-o",
        str(source_dir / "%(title).80s-%(id)s.%(ext)s"),
    ]
    active_cookies = cookies or (
        Path(os.environ["VIDEO_DOWNLOADER_COOKIES_PATH"])
        if os.environ.get("VIDEO_DOWNLOADER_COOKIES_PATH")
        else None
    )
    active_proxy = proxy or os.environ.get("VIDEO_DOWNLOADER_PROXY")
    if active_cookies:
        if not active_cookies.is_file():
            raise SkillError(
                "cookies_missing",
                "配置的 Cookie 文件不存在。",
                {"path": str(active_cookies)},
            )
        args.extend(["--cookies", str(active_cookies)])
    if active_proxy:
        args.extend(["--proxy", active_proxy])
    args.append(url)
    result = run(args, "download_failed", "视频下载失败。")
    paths = [Path(line.strip()) for line in result.stdout.splitlines() if line.strip()]
    media_path = next((path for path in reversed(paths) if path.is_file()), None)
    if media_path is None:
        candidates = sorted(source_dir.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
        media_path = next((path for path in candidates if path.is_file()), None)
    if media_path is None:
        raise SkillError("download_output_missing", "下载命令结束后没有找到视频文件。")
    resolved = media_path.resolve()
    return {
        "source_kind": "downloaded_url",
        "original_input": original_input,
        "resolved_url": url,
        "platform": platform_name(url),
        "local_path": str(resolved),
        "file_name": resolved.name,
        "size_bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }


def resolve(args: argparse.Namespace) -> dict[str, object]:
    original_input = args.source.strip()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = Path(original_input).expanduser()
    if path.is_file() or looks_like_local_path(original_input):
        source_media = local_source(path, original_input, args.output_dir)
    else:
        match = URL_PATTERN.search(original_input)
        if not match:
            raise SkillError(
                "source_unrecognized",
                "输入中没有找到本地视频路径或 HTTP(S) 链接。",
            )
        source_media = downloaded_source(
            original_input,
            match.group(0).rstrip("，。！？,.!?；;"),
            args.output_dir,
            args.cookies,
            args.proxy,
        )
    write_json(args.output_dir / "source.json", {"schema_version": "1.0", **source_media})
    return source_media


def main() -> int:
    try:
        args = build_parser().parse_args()
        emit({"ok": True, "source_media": resolve(args)})
        return 0
    except SkillError as error:
        return fail(error)


if __name__ == "__main__":
    sys.exit(main())
