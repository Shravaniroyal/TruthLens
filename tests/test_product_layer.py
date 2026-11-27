"""Product-layer tests that do not load the forensic model or call gov APIs."""

from __future__ import annotations

import io
import unittest

from PIL import Image

from truthlens.bgv import evaluate_workflow
from truthlens.doc_types import detect_doc_type
from truthlens.fields import extract_fields, mask_aadhaar, mask_pan
from truthlens.official import cross_verify
from truthlens.quality import assess_quality
from truthlens.security import redact_secrets, validate_upload


def _png_bytes(size: tuple[int, int] = (120, 80), color: tuple[int, int, int] = (40, 80, 40)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return buf.getvalue()


class FieldTests(unittest.TestCase):
    def test_pan_extract_and_mask(self):
        fields = extract_fields("Permanent Account Number ABCDE1234F")
        self.assertNotEqual(mask_pan("ABCDE1234F"), "ABCDE1234F")
        self.assertNotIn("ABCDE1234F", str(fields.to_public_dict()))

    def test_aadhaar_masking(self):
        self.assertNotEqual(mask_aadhaar("234567890123"), "234567890123")

    def test_redact_does_not_keep_full_ids(self):
        text = redact_secrets("Aadhaar 2345 6789 0123 PAN ABCDE1234F")
        self.assertNotIn("2345", text.replace("XXXX", ""))
        self.assertNotIn("ABCDE1234F", text)


class DocTypeAndBgvTests(unittest.TestCase):
    def test_filename_pan(self):
        self.assertEqual(detect_doc_type("pan_card.jpg"), "pan")

    def test_ocr_marksheet(self):
        self.assertEqual(detect_doc_type("scan.jpg", "CBSE Marksheet 2024"), "marksheet")

    def test_job_joining_complete_and_missing(self):
        ok = evaluate_workflow("job_joining", ["pan", "aadhaar", "degree"])
        self.assertTrue(ok.complete)
        missing = evaluate_workflow("job_joining", ["aadhaar"])
        self.assertIn("pan", missing.missing_required)
        self.assertFalse(missing.complete)

    def test_college_admission(self):
        status = evaluate_workflow("college_admission", ["aadhaar", "marksheet"])
        self.assertTrue(status.complete)


class OfficialStubTests(unittest.TestCase):
    def test_not_configured_without_keys(self):
        result = cross_verify(extract_fields("PAN ABCDE1234F"))
        self.assertEqual(result.status, "not_configured")
        self.assertIsNone(result.matched)


class QualityAndUploadTests(unittest.TestCase):
    def test_sharp_image_usable(self):
        img = Image.new("RGB", (64, 64), (128, 128, 128))
        report = assess_quality(img)
        self.assertIn("usable", report.to_dict())

    def test_png_upload_ok(self):
        data = _png_bytes()
        validated = validate_upload(data, "sample.png")
        self.assertEqual(validated.extension, "png")
        self.assertEqual(validated.media_kind, "image")
        self.assertEqual(len(validated.content_hash), 64)

    def test_pdf_magic_accepted(self):
        payload = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n"
        validated = validate_upload(payload, "form.pdf")
        self.assertEqual(validated.media_kind, "pdf")

    def test_bad_extension_rejected(self):
        from truthlens.exceptions import SecurityValidationError

        with self.assertRaises(SecurityValidationError):
            validate_upload(b"not-an-image", "virus.exe")


class ApiHealthTests(unittest.TestCase):
    def test_health_and_workflows(self):
        from fastapi.testclient import TestClient

        from truthlens.api import create_app

        client = TestClient(create_app())
        health = client.get("/health")
        self.assertEqual(health.status_code, 200)
        body = health.json()
        self.assertTrue(body["ok"])
        self.assertEqual(body["official_status"], "not_configured")
        wf = client.get("/v1/workflows")
        self.assertEqual(wf.status_code, 200)
        self.assertIn("job_joining", wf.json()["workflows"])


if __name__ == "__main__":
    unittest.main()