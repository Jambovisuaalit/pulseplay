from __future__ import annotations

import json
import re
from pathlib import Path

import pdfplumber
import pytesseract

MAX_CHARS = 12_000
ATTACHMENT_DIR = Path("/tmp/attachments")
OUTPUT_PATH = Path("data/attachment_texts.json")


def clean_text(text: str, max_chars: int = MAX_CHARS) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text[:max_chars]


def extract_single_pdf(pdf_path: Path) -> dict[str, str]:
    parts: list[str] = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""

                if page_text.strip():
                    parts.append(page_text)
                else:
                    image = page.to_image(resolution=200).original
                    ocr_text = pytesseract.image_to_string(
                        image,
                        lang="fin+eng",
                    )
                    if ocr_text.strip():
                        parts.append(ocr_text)

                if sum(len(part) for part in parts) >= MAX_CHARS * 1.2:
                    break
    except Exception as exc:
        print(f"Failed {pdf_path.name}: {exc}")

    return {
        "filename": pdf_path.name,
        "clean_text": clean_text("\n".join(parts)),
    }


def extract_attachment_texts(
    folder: Path = ATTACHMENT_DIR,
) -> list[dict[str, str]]:
    if not folder.exists():
        return []

    return [
        extract_single_pdf(path)
        for path in sorted(folder.glob("*.pdf"))
    ]


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    documents = extract_attachment_texts()
    OUTPUT_PATH.write_text(
        json.dumps(documents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {len(documents)} extracted documents to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
