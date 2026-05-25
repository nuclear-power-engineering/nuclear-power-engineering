#!/usr/bin/env python3
"""Extract structured text from a journal article PDF.

Usage: python3 extract_pdf.py <pdf_path>

Outputs JSON with extracted fields.
"""

import json
import re
import sys

from PyPDF2 import PdfReader


def extract_pdf(pdf_path: str) -> dict:
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)

    all_pages = []
    for page in reader.pages:
        all_pages.append(page.extract_text())

    all_text = "\n".join(all_pages)
    first_page = all_pages[0]
    last_pages = all_pages[max(0, total_pages - 4):]
    last_text = "\n".join(last_pages)

    result = {
        "total_pages": total_pages,
        "first_page_text": first_page,
        "last_pages_text": last_text,
        "full_text": all_text,
    }

    # Extract UDC from first page
    udc_match = re.search(r"УДК\s+([\d.]+)", first_page)
    if udc_match:
        result["udc"] = udc_match.group(1)

    # Extract DOI from first page
    doi_match = re.search(r"DOI[:\s]*https?://doi\.org/[\d./\w]+", first_page, re.IGNORECASE)
    if doi_match:
        result["doi"] = doi_match.group(0).replace("DOI : ", "").replace("DOI:", "").strip()

    # Extract rubric from first page
    rubric_match = re.search(
        r"([А-ЯЁ\s]+)\s*/\s*([A-Z\s]+)",
        first_page,
    )
    if rubric_match:
        result["rubric_ru"] = rubric_match.group(1).strip()
        result["rubric_en"] = rubric_match.group(2).strip()

    # Extract first page number
    first_page_num = re.match(r"(\d+)", first_page.strip())
    if first_page_num:
        result["first_page"] = first_page_num.group(1)

    # Extract last page number from last page
    last_page_num = re.match(r"(\d+)", last_pages[-1].strip()) if last_pages else None
    if last_page_num:
        result["last_page"] = last_page_num.group(1)

    # Find the RU "Авторы" section (between "Авторы" heading and the EN section)
    authors_ru_match = re.search(
        r"Авторы\n(.+?)(?=\nUDC|\nДля цитирования|\nДля\u00a0цитирования|\nAbstract|\Z)",
        all_text,
        re.DOTALL,
    )
    if authors_ru_match:
        result["authors_ru_text"] = authors_ru_match.group(1).strip()

    # Find the EN "Authors" section
    authors_en_match = re.search(
        r"Authors?\n(.+?)(?=\n$|\Z)",
        last_text,
        re.DOTALL,
    )
    if authors_en_match:
        result["authors_en_text"] = authors_en_match.group(1).strip()

    return result


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 extract_pdf.py <pdf_path>", file=sys.stderr)
        sys.exit(1)

    data = extract_pdf(sys.argv[1])
    print(json.dumps(data, ensure_ascii=False, indent=2))
