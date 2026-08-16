#!/usr/bin/env python3
"""Extract text from a scanned (image-based) PDF using OCR.

PyMuPDF renders each page to an image, then pytesseract (Tesseract OCR)
extracts Japanese text from the image.

前提: Tesseract OCR本体（日本語データ jpn.traineddata 込み）がシステムに
インストールされている必要があります。インストール方法は README 参照。
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

import fitz  # PyMuPDF
import pytesseract
from PIL import Image

HAMAKURU_DIR = Path(__file__).parent.parent / "hamakuru"
TESSDATA_DIR = Path(__file__).parent / "tessdata"

# 解像度倍率（1.0 = 72dpi相当）。数字を上げるほどOCR精度が上がるが処理は遅くなる。
ZOOM = 3.0


def find_tesseract() -> str | None:
    exe = shutil.which("tesseract")
    if exe:
        return exe
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ):
        if Path(candidate).exists():
            return candidate
    return None


def ocr_pdf(pdf_path: Path, lang: str = "jpn") -> str:
    pages_text: list[str] = []
    doc = fitz.open(pdf_path)
    matrix = fitz.Matrix(ZOOM, ZOOM)
    try:
        for i, page in enumerate(doc, start=1):
            pix = page.get_pixmap(matrix=matrix)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            text = pytesseract.image_to_string(img, lang=lang)
            if text.strip():
                pages_text.append(f"--- ページ {i} ---\n{text.strip()}")
            print(f"[OCR完了] ページ {i}/{len(doc)}", file=sys.stderr)
    finally:
        doc.close()
    return "\n\n".join(pages_text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "pdf",
        nargs="?",
        default="gaidorinezenbun.pdf",
        help="hamakuru フォルダー内のPDFファイル名（デフォルト: gaidorinezenbun.pdf）",
    )
    parser.add_argument("--lang", default="jpn", help="Tesseract言語コード（デフォルト: jpn）")
    args = parser.parse_args()

    tesseract_cmd = find_tesseract()
    if tesseract_cmd is None:
        print(
            "エラー: Tesseract OCRが見つかりません。インストールしてから再実行してください。\n"
            "  winget install --id UB-Mannheim.TesseractOCR\n"
            "インストール後、日本語データ (jpn.traineddata) が含まれているか確認してください。",
            file=sys.stderr,
        )
        sys.exit(1)
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    # 同梱の tessdata/jpn.traineddata を優先し、システム標準の言語データ配置に依存しない
    if TESSDATA_DIR.exists():
        os.environ["TESSDATA_PREFIX"] = str(TESSDATA_DIR)

    pdf_path = HAMAKURU_DIR / args.pdf
    if not pdf_path.exists():
        print(f"エラー: ファイルが見つかりません: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[OCR開始] {pdf_path.name} ...", file=sys.stderr)
    text = ocr_pdf(pdf_path, lang=args.lang)

    output_path = HAMAKURU_DIR / f"{pdf_path.stem}_ocr.txt"
    output_path.write_text(text, encoding="utf-8")
    print(f"\n完了: {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
