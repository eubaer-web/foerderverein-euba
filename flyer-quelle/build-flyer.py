#!/usr/bin/env python3
"""
Baut aus flyer-a5.html die drei Flyer-PDFs:

  flyer-foerderverein-a5.pdf        148 x 210 mm  – Original zum Auslegen
  flyer-foerderverein-a4.pdf        210 x 297 mm  – vergroessert als Aushang
  flyer-foerderverein-a4-2fach.pdf  297 x 210 mm  – 2 x A5 auf A4 quer zum Ausschneiden

Voraussetzungen:  pip3 install pypdf pypdfium2   (Google Chrome muss installiert sein)
Aufruf:           python3 flyer-quelle/build-flyer.py

Warum der Umweg ueber pypdf statt CSS-transform:
Chrome druckt die Seite minimal groesser als das CSS-Layoutfenster – dadurch bleibt am Rand ein
weisser Haarstreifen stehen. Die A4-Fassungen werden deshalb nicht im Browser skaliert, sondern
aus dem fertigen A5-PDF. Anschliessend wird der Inhalt anhand seiner gemessenen Bounding-Box
exakt auf das Seitenformat eingepasst, damit alle vier Kanten randlos sind.
"""

import os
import shutil
import subprocess
import sys
import time

from pypdf import PdfReader, PdfWriter, Transformation, PageObject
from pypdf.generic import RectangleObject
import pypdfium2 as pdfium

MM = 72 / 25.4
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)          # Webseiten-Wurzel
SRC_HTML = os.path.join(HERE, "flyer-a5.html")
A5 = os.path.join(OUT, "flyer-foerderverein-a5.pdf")
A4 = os.path.join(OUT, "flyer-foerderverein-a4.pdf")
A4_2X = os.path.join(OUT, "flyer-foerderverein-a4-2fach.pdf")

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
RENDER_SCALE = 8                     # Aufloesung der Randkontrolle


def html_to_pdf(html_path, pdf_path):
    """Chrome headless rendert die HTML-Datei nach PDF."""
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    proc = subprocess.Popen(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--user-data-dir=/tmp/flyer-build-{os.getpid()}",
         f"--print-to-pdf={pdf_path}", f"file://{html_path}"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    # Chrome beendet sich nach dem Druck nicht zuverlaessig -> auf die Datei warten
    for _ in range(60):
        time.sleep(1)
        if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 0:
            time.sleep(2)
            break
    proc.terminate()
    if not os.path.exists(pdf_path):
        sys.exit(f"FEHLER: {pdf_path} wurde nicht erzeugt")


def content_bbox(pdf_path):
    """Bounding-Box des sichtbaren Inhalts in PDF-Punkten (links, unten, rechts, oben)."""
    page = PdfReader(pdf_path).pages[0]
    w, h = float(page.mediabox.width), float(page.mediabox.height)
    img = pdfium.PdfDocument(pdf_path)[0].render(scale=RENDER_SCALE).to_pil().convert("RGB")
    iw, ih = img.size
    px = img.load()

    def is_white(c):
        return c[0] > 250 and c[1] > 250 and c[2] > 250

    cols = [x for x in range(iw) if any(not is_white(px[x, y]) for y in range(ih))]
    rows = [y for y in range(ih) if any(not is_white(px[x, y]) for x in range(iw))]
    x0, x1, y0, y1 = cols[0], cols[-1], rows[0], rows[-1]

    return (x0 / iw * w, h - (y1 + 1) / ih * h, (x1 + 1) / iw * w, h - y0 / ih * h), w, h


def fit_to_page(pdf_path):
    """Zieht den Inhalt so, dass er die Seite exakt randlos ausfuellt."""
    (left, bottom, right, top), w, h = content_bbox(pdf_path)
    page = PdfReader(pdf_path).pages[0]
    page.add_transformation(
        Transformation().translate(-left, -bottom).scale(w / (right - left), h / (top - bottom))
    )
    page.mediabox = RectangleObject((0, 0, w, h))
    page.cropbox = RectangleObject((0, 0, w, h))
    out = PageObject.create_blank_page(width=w, height=h)
    out.merge_page(page)
    writer = PdfWriter()
    writer.add_page(out)
    with open(pdf_path, "wb") as f:
        writer.write(f)


def a5_scaled_to(dst_w, dst_h, x_offset=0):
    """Liefert die A5-Seite, skaliert auf die Zielgroesse."""
    page = PdfReader(A5).pages[0]
    sw, sh = float(page.mediabox.width), float(page.mediabox.height)
    page.add_transformation(
        Transformation().scale(dst_w / sw, dst_h / sh).translate(x_offset, 0)
    )
    page.mediabox = RectangleObject((0, 0, max(dst_w + x_offset, dst_w), dst_h))
    page.cropbox = page.mediabox
    return page


def write_single(path, w, h, pages):
    canvas = PageObject.create_blank_page(width=w, height=h)
    for p in pages:
        p.mediabox = RectangleObject((0, 0, w, h))
        p.cropbox = RectangleObject((0, 0, w, h))
        canvas.merge_page(p)
    writer = PdfWriter()
    writer.add_page(canvas)
    with open(path, "wb") as f:
        writer.write(f)


def check(path):
    (left, bottom, right, top), w, h = content_bbox(path)
    name = os.path.basename(path)
    print(f"  {name:36s} {w/MM:5.0f} x {h/MM:5.0f} mm   "
          f"Rand L{left/MM:.2f} R{(w-right)/MM:.2f} O{(h-top)/MM:.2f} U{bottom/MM:.2f} mm")


def main():
    if not shutil.which(CHROME) and not os.path.exists(CHROME):
        sys.exit("FEHLER: Google Chrome nicht gefunden")

    print("1/4  A5 aus HTML rendern ...")
    html_to_pdf(SRC_HTML, A5)
    fit_to_page(A5)

    print("2/4  A4 hoch aufbauen ...")
    write_single(A4, 210 * MM, 297 * MM, [a5_scaled_to(210 * MM, 297 * MM)])
    fit_to_page(A4)

    print("3/4  A4 quer mit 2 x A5 aufbauen ...")
    half = (297 * MM) / 2
    write_single(A4_2X, 297 * MM, 210 * MM,
                 [a5_scaled_to(half, 210 * MM, 0), a5_scaled_to(half, 210 * MM, half)])

    print("4/4  Randkontrolle:")
    for p in (A5, A4, A4_2X):
        check(p)
    print("\nFertig. Danach: git add + commit + push, damit es auf der Website live geht.")


if __name__ == "__main__":
    main()
