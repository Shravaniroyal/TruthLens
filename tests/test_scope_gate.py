from types import SimpleNamespace

from truthlens.pipeline import apply_scope_gate


def _a(label):
    return SimpleNamespace(verdict=SimpleNamespace(label=label))


def test_pdf_fake_is_capped():
    a, note = apply_scope_gate(_a("FAKE"), "pdf", "marksheet")
    assert a.verdict.label == "UNCERTAIN" and note


def test_unsupported_type_image_capped():
    a, _ = apply_scope_gate(_a("FAKE"), "image", "generic")
    assert a.verdict.label == "UNCERTAIN"


def test_validated_image_unchanged():
    a, note = apply_scope_gate(_a("FAKE"), "image", "pan")
    assert a.verdict.label == "FAKE" and note == ""
