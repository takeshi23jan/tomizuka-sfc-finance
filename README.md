# tomizuka-sfc-finance
静岡県浜松市富塚地区男子ソフトテニスクラブ会計についてまとめるrepositoryです

## ファイル構成

### brain storm/
| ファイル | 説明 |
|---|---|
| `AccountingCalendar.md` | 会計年度スケジュール・締め日などの年間カレンダー案 |
| `BudgetProposal.md` | 予算案の検討メモ |
| `CityInquiries.md` | 浜松市への問い合わせ内容まとめ |
| `FinancePlanStudy.md` | 会計制度・運営方針の調査・検討メモ |
| `NakamuraSanRequest.md` | 中村さんからの依頼事項まとめ |
| `PurchaseAndSubsidy.md` | 購入品・補助金申請に関する検討メモ |
| `RecordManagement.md` | 帳票・記録管理方針の検討メモ |
| `WithholdingTax.md` | 源泉徴収に関する調査・検討メモ |
| `予算案.ods` | 予算案スプレッドシート |

### supplement/


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


### supplement/
| ファイル | 説明 |
|---|---|
| `2025年度収支報告書(父母会).pdf` | 2025年度 富塚中男子ソフトテニス部父母の会 収支報告 |



作成: 桑原 武(with GitHub Copilot Claude Sonnet 4.6)