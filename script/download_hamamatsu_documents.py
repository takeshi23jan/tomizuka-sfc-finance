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
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr_map = dict(attrs)
        href = attr_map.get("href")
        if href:
            self.links.append(href)


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

    unique_links: list[str] = []
    seen: set[str] = set()
    for href in parser.links:
        full_url = urljoin(TARGET_URL, href)
        if full_url in seen:
            continue
        seen.add(full_url)
        if looks_like_download_link(href):
            unique_links.append(full_url)

    if not unique_links:
        print("No downloadable links were found.")
        return 1

    print(f"Found {len(unique_links)} downloadable links.")
    for index, url in enumerate(unique_links, start=1):
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
        except (HTTPError, URLError) as exc:
            print(f"[{index}/{len(unique_links)}] Failed: {url} ({exc})")

    print(f"Files saved in: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
