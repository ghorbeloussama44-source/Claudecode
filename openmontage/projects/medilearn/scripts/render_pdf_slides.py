"""Rasterize pages from the client's slide deck PDF into JPEGs for Remotion.

The deck has no extractable text (vector/image slides) — always rasterize
and look at them, don't try page.get_text().

Usage:
    python3 render_pdf_slides.py 5 6 7 8
    # writes remotion-composer/public/medilearn/slides/slide_05.jpg etc.
"""
import sys
from pathlib import Path

import pymupdf
from PIL import Image

ROOT = Path("/home/user/Claudecode/openmontage")
PDF = ROOT / "projects/medilearn/assets/originals/Mastering_Hypertension_2024.pdf"
OUT_DIR = ROOT / "remotion-composer/public/medilearn/slides"


def render(page_numbers: list[int]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(PDF)
    for n in page_numbers:
        page = doc[n - 1]  # 1-indexed on the command line
        pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))
        tmp_png = OUT_DIR / f"slide_{n:02d}_tmp.png"
        pix.save(tmp_png)
        im = Image.open(tmp_png).convert("RGB")
        im.save(OUT_DIR / f"slide_{n:02d}.jpg", quality=90)
        tmp_png.unlink()
        print(f"slide_{n:02d}.jpg  ({im.size[0]}x{im.size[1]})")


if __name__ == "__main__":
    pages = [int(a) for a in sys.argv[1:]]
    if not pages:
        print("usage: render_pdf_slides.py <page_number> [page_number ...]")
        sys.exit(1)
    render(pages)
