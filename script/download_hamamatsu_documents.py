#!/usr/bin/env python3
"""Download document links found on the Hamamatsu City page."""
from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen

TARGET_URL = "https://www.city.hamamatsu.shizuoka.jp/renkei/tiikitenkai.html"
DOWNLOAD_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".xlsm",
    ".ppt",
    ".pptx",
    ".zip",
    ".csv",
    ".txt",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".odt",
    ".rtf",
}
SKIP_HOSTS = {"youtu.be", "www.youtube.com", "youtube.com"}

class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self._anchor_stack: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href:
            self._anchor_stack.append({"href": href, "text": ""})

    def handle_data(self, data: str) -> None:
        if self._anchor_stack:
            self._anchor_stack[-1]["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._anchor_stack:
            return
        self.links.append(self._anchor_stack.pop())


def sanitize_filename(name: str) -> str:
    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._-")
    return safe_name or "downloaded_file"


def looks_like_download_link(href: str) -> bool:
    if not href or href.startswith("#"):
        return False

    parsed = urlparse(href)
    if parsed.scheme in {"mailto", "tel"}:
        return False

    if parsed.netloc.lower() in SKIP_HOSTS:
        return False

    path = unquote(parsed.path).lower()
    suffix = Path(path).suffix
    return suffix in DOWNLOAD_EXTENSIONS


def download_file(url: str, destination: Path) -> None:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(request) as response:
        destination.write_bytes(response.read())


def build_mapping_markdown(entries: list[dict[str, str]], target_url: str) -> str:
    lines = [
        "# Hamamatsu document download mapping",
        "",
        f"Source page: {target_url}",
        "",
        "| 保存ファイル | 対応元リンク | 表示文言 |",
        "| --- | --- | --- |",
    ]

    if not entries:
        lines.append("| なし | なし | なし |")
        return "\n".join(lines) + "\n"

    for entry in entries:
        filename = entry["filename"].replace("|", "\\|")
        source_url = entry["source_url"].replace("|", "\\|")
        display_text = re.sub(r"\s+", " ", entry["display_text"]).strip() or "(表示文言なし)"
        lines.append(f"| {filename} | {source_url} | {display_text} |")

    return "\n".join(lines) + "\n"


def main() -> int:
    output_dir = Path(__file__).resolve().parents[1] / "hamakuru"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        request = Request(TARGET_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request) as response:
            html = response.read().decode("utf-8", errors="replace")
    except (HTTPError, URLError) as exc:
        print(f"Failed to fetch the target page: {exc}", file=sys.stderr)
        return 1

    parser = LinkParser()
    parser.feed(html)
    parser.close()

    unique_links: list[tuple[str, str]] = []
    seen: set[str] = set()
    for link in parser.links:
        href = link["href"]
        full_url = urljoin(TARGET_URL, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        if looks_like_download_link(href):
            unique_links.append((full_url, link["text"]))

    if not unique_links:
        print("No downloadable .links were found.")
        return 1

    print(f"Found {len(unique_links)} downloadable links.")
    mapping_entries: list[dict[str, str]] = []
    for index, (url, link_text) in enumerate(unique_links, start=1):
        parsed = urlparse(url)
        filename = sanitize_filename(Path(unquote(parsed.path)).name or f"file_{index}")
        destination = output_dir / filename

        counter = 1
        while destination.exists():
            stem = Path(filename).stem
            suffix = Path(filename).suffix
            destination = output_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        try:
            download_file(url, destination)
            print(f"[{index}/{len(unique_links)}] Downloaded: {destination.name}")
            mapping_entries.append(
                {
                    "filename": destination.name,
                    "source_url": url,
                    "display_text": link_text,
                }
            )
        except (HTTPError, URLError) as exc:
            print(f"[{index}/{len(unique_links)}] Failed: {url} ({exc})")

    mapping_path = output_dir / "document_mapping.md"
    mapping_path.write_text(build_mapping_markdown(mapping_entries, TARGET_URL), encoding="utf-8")
    print(f"Mapping summary saved in: {mapping_path}")
    print(f"Files saved in: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
