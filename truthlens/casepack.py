"""
PDF case pack for a TruthLens batch (BGV) run.

Contains: file verdicts, missing required documents, reviewer decisions,
sign-off lines and the screening disclaimer. Only masked/summary data is
used. Never pass full Aadhaar / PAN numbers in.

Needs: pip install reportlab
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Any, Iterable
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from truthlens.official import DISCLAIMER

SCREENING_NOTE = (
    "This pack records visual tamper screening and checklist completeness only. "
    "It is not legal KYC and not UIDAI or issuer verification. Confirm important "
    "documents with the issuing authority."
)

_base = getSampleStyleSheet()
_body = ParagraphStyle("body", parent=_base["BodyText"], fontSize=9.5, leading=13)
_cell = ParagraphStyle("cell", parent=_base["BodyText"], fontSize=8.5, leading=11)
_hdr = ParagraphStyle("hdr", parent=_cell, textColor=colors.white, fontName="Helvetica-Bold")
_h1 = ParagraphStyle("h1", parent=_base["Title"], fontSize=20, spaceAfter=4, alignment=0)
_h2 = ParagraphStyle("h2", parent=_base["Heading2"], fontSize=12.5, spaceBefore=12, spaceAfter=6)
_small = ParagraphStyle("small", parent=_body, fontSize=8, textColor=colors.HexColor("#555555"))


def _txt(value: Any) -> str:
    return escape(str(value)) if value not in (None, "") else "—"


def _table(head: list[str], body: list[list[Any]], widths_mm: list[float],
           header_bg: str = "#1f2a44", row_height_mm: float | None = None) -> Table:
    data = [[Paragraph(escape(h), _hdr) for h in head]]
    data += [[Paragraph(_txt(c), _cell) for c in row] for row in body]
    heights = None
    if row_height_mm is not None:
        heights = [None] + [row_height_mm * mm] * len(body)
    t = Table(data, colWidths=[w * mm for w in widths_mm], rowHeights=heights, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8bfcc")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f5f9")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def _outcome(complete: bool, rows: list[dict], items: list[Any]) -> tuple[str, str]:
    if not complete:
        return "INCOMPLETE", "Required documents are missing."
    queued = {i.filename for i in items}
    unqueued = [
        r for r in rows
        if str(r.get("verdict", "")).upper() in ("FAKE", "UNCERTAIN") and r.get("file") not in queued
    ]
    if unqueued:
        return "PENDING REVIEW", f"{len(unqueued)} flagged file(s) have no reviewer decision on record."
    pending = [i for i in items if i.status == "pending"]
    if pending:
        return "PENDING REVIEW", f"{len(pending)} flagged file(s) still need a reviewer decision."
    blocked = [i for i in items if i.status in ("rejected", "need_original")]
    if blocked:
        return "ACTION NEEDED", f"{len(blocked)} file(s) were rejected or need the original."
    return "SCREENING CLEAR", "All required documents present and no open flags. Screening only, not verification."


def _footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(15 * mm, 10 * mm, "TruthLens v5 case pack — visual screening only, not legal KYC")
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def build_case_pack(
    *,
    case_id: str,
    workflow_label: str,
    operator: str,
    rows: list[dict],
    complete: bool,
    missing: Iterable[str],
    items: list[Any],
) -> bytes:
    """Return the case pack as PDF bytes.

    rows  : batch table rows with keys file, type, slot, verdict, qr
    items : ReviewItem objects for this case (any status)
    """
    missing = list(missing)
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=18 * mm,
        title=f"TruthLens case {case_id}", author="TruthLens",
    )
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story: list[Any] = [
        Paragraph("TruthLens — Case Pack", _h1),
        Paragraph(escape(f"Case {case_id} · {workflow_label}"), _body),
        Paragraph(escape(f"Operator: {operator or '—'} · Generated: {now}"), _small),
        Spacer(1, 6),
    ]

    label, detail = _outcome(complete, rows, items)
    story += [
        Paragraph("Screening outcome", _h2),
        Paragraph(f"<b>{escape(label)}</b> — {escape(detail)}", _body),
        Paragraph("Documents screened", _h2),
        _table(
            ["File", "Type", "Slot", "Verdict", "QR"],
            [[r.get("file"), r.get("type"), r.get("slot"), r.get("verdict"), r.get("qr")] for r in rows],
            [58, 36, 28, 40, 14],
        ),
        Paragraph("Required documents", _h2),
        Paragraph(
            ("<b>Missing:</b> " + escape(", ".join(missing)))
            if missing else "All required slots for this workflow are present.",
            _body,
        ),
        Paragraph("Reviewer decisions", _h2),
    ]

    if items:
        story.append(
            _table(
                ["File", "Verdict", "Status", "Reviewer", "Decided (UTC)", "Note"],
                [[i.filename, f"{i.verdict} {i.confidence:.0f}%", i.status, i.reviewer,
                  i.decided_at.replace("T", " "), i.note] for i in items],
                [34, 24, 24, 26, 30, 42],
                header_bg="#3a2a44",
            )
        )
    else:
        story.append(Paragraph("No files were flagged for review.", _body))

    story += [
        Spacer(1, 18),
        Paragraph("Sign-off", _h2),
        _table(["Reviewer name", "Signature", "Date"], [[" ", " ", " "]], [70, 70, 38], row_height_mm=16),
        Spacer(1, 14),
        Paragraph("Important", _h2),
        Paragraph(escape(SCREENING_NOTE), _body),
        Spacer(1, 4),
        Paragraph(escape(DISCLAIMER), _small),
    ]

    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return buf.getvalue()
