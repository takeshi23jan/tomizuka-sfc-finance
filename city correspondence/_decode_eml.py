"""eml decoding helper for the city correspondence folder.

Decodes all *.eml files in this folder (quoted-printable / base64 MIME
encoded Japanese email) into a single readable UTF-8 text file, so the
content can be reviewed without dealing with raw MIME encoding.

Usage:
    python decode_eml_temp.py

Output:
    decoded_output.txt is (re)generated in this same folder.
    This output file is temporary/disposable - do not commit it.
"""

from email import message_from_binary_file, policy
from email.message import Message
from pathlib import Path


def extract_body(msg: Message) -> str:
    if msg.is_multipart():
        plain_part = None
        html_part = None
        for part in msg.walk():
            if part.is_multipart():
                continue
            disposition = str(part.get("Content-Disposition") or "")
            if "attachment" in disposition:
                continue
            content_type = part.get_content_type()
            if content_type == "text/plain" and plain_part is None:
                plain_part = part
            elif content_type == "text/html" and html_part is None:
                html_part = part
        chosen = plain_part or html_part
        if chosen is None:
            return "(本文が見つかりませんでした)"
        return chosen.get_content()
    return msg.get_content()


def main() -> None:
    folder = Path(__file__).parent
    eml_files = sorted(folder.glob("*.eml"))

    out_path = folder / "decoded_output.txt"
    with out_path.open("w", encoding="utf-8") as out:
        for eml_path in eml_files:
            with eml_path.open("rb") as fh:
                msg = message_from_binary_file(fh, policy=policy.default)

            print("=" * 100, file=out)
            print(f"FILE: {eml_path.name}", file=out)
            print("=" * 100, file=out)
            print(f"From: {msg.get('From')}", file=out)
            print(f"To: {msg.get('To')}", file=out)
            print(f"Date: {msg.get('Date')}", file=out)
            print(f"Subject: {msg.get('Subject')}", file=out)
            print("-" * 100, file=out)
            print(extract_body(msg), file=out)
            print("\n", file=out)

    print(f"Decoded {len(eml_files)} file(s) to {out_path}")


if __name__ == "__main__":
    main()
