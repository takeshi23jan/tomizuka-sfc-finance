#!/usr/bin/env python3
"""Extract text from priority accounting-related PDFs in the hamakuru folder."""
from __future__ import annotations

from pathlib import Path

import pdfplumber

HAMAKURU_DIR = Path(__file__).parent.parent / "hamakuru"
OUTPUT_FILE = HAMAKURU_DIR / "pdf_text_extraction.txt"

# 会計担当向け優先6ファイル
PRIORITY_PDFS = [
    ("furo-cha-to.pdf", "はまクル認定クラブ申請フローチャート"),
    ("hojokinn.pdf", "はまクル認定クラブに関する補助金制度の概要"),
    ("10hojokintebiki.pdf", "はまクル認定クラブ活動支援事業費補助金制度の手引き"),
    ("11gensentebiki.pdf", "源泉徴収の手引き"),
    ("12faqkihon.pdf", "補助金制度Q＆A集【基本編】"),
    ("13faqkobetu.pdf", "補助金制度Q＆A集【個別課題編】"),
]


def extract_pdf_text(pdf_path: Path) -> str:
    pages_text: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text:
                pages_text.append(f"--- ページ {i} ---\n{text.strip()}")
    return "\n\n".join(pages_text)


def main() -> None:
    lines: list[str] = []
    for filename, title in PRIORITY_PDFS:
        pdf_path = HAMAKURU_DIR / filename
        if not pdf_path.exists():
            print(f"[SKIP] ファイルが見つかりません: {filename}")
            continue
        print(f"[読み取り中] {filename} ...")
        text = extract_pdf_text(pdf_path)
        lines.append(f"{'=' * 60}")
        lines.append(f"ファイル: {filename}")
        lines.append(f"タイトル: {title}")
        lines.append(f"{'=' * 60}")
        lines.append(text)
        lines.append("")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n完了: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
