import io
import logging
import re

from PIL import Image, ImageDraw

from truthlens.pipeline import analyze_document


class _Cap(logging.Handler):
    def __init__(self):
        super().__init__(logging.DEBUG)
        self.lines = []

    def emit(self, record):
        self.lines.append(record.getMessage())


def test_no_pii_in_logs():
    img = Image.new("RGB", (900, 600), "white")
    d = ImageDraw.Draw(img)
    d.text((40, 80), "Ramesh Kumar 1234 5678 9012", fill="black")
    d.text((40, 160), "ABCDE1234F", fill="black")
    buf = io.BytesIO()
    img.save(buf, "PNG")

    lg = logging.getLogger("truthlens")
    cap = _Cap()
    old = lg.level
    lg.setLevel(logging.DEBUG)
    lg.addHandler(cap)
    try:
        analyze_document(buf.getvalue(), "Ramesh_123456789012_ABCDE1234F.png", run_model=False)
    finally:
        lg.removeHandler(cap)
        lg.setLevel(old)

    text = "\n".join(cap.lines)
    assert text, "no log lines captured"
    assert not re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text)
    assert not re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
    assert "Ramesh" not in text
