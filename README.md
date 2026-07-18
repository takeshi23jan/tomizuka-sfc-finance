# tomizuka-sfc-finance
静岡県浜松市富塚地区男子ソフトテニスクラブ会計についてまとめるrepositoryです

## ファイル構成

### script/
| ファイル | 説明 |
|---|---|
| `download_hamamatsu_documents.py` | 浜松市公式ページから地域クラブ関連資料を一括ダウンロードするスクリプト |
| `pdf_reader.py` | `hamakuru/`フォルダー内の会計関連PDFからテキストを抽出し、`hamakuru/pdf_text_extraction.txt`に出力するスクリプト。`uv run python pdf_reader.py`で実行 |
| `pyproject.toml` | uv仮想環境の設定ファイル（依存ライブラリ: `pdfplumber`） |

### hamakuru/
| ファイル | 説明 |
|---|---|
| `pdf_text_extraction.txt` | `pdf_reader.py`が生成する抽出テキストファイル。会計関連優先6PDFの内容をまとめたもの（フローチャート・補助金概要・手引き・源泉徴収・FAQ基本・FAQ個別） |
| `document_mapping.md` | ダウンロード済みファイルと元URLの対応表 |
