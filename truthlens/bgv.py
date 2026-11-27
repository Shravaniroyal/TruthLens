"""Background-verification checklists for college, employment, and vendor KYC."""

from __future__ import annotations

from dataclasses import dataclass

WORKFLOWS: dict[str, dict[str, object]] = {
    "college_admission": {
        "label": "College admissions",
        "required": ["photo_id", "marksheet"],
        "optional": ["caste_income"],
    },
    "job_joining": {
        "label": "Job joining / HR BGV",
        "required": ["pan", "photo_id", "degree"],
        "optional": ["experience_letter"],
    },
    "vendor_kyc": {
        "label": "Vendor / tender KYC",
        "required": ["pan", "company_doc"],
        "optional": ["cancelled_cheque"],
    },
}

# Maps detected doc_type → BGV slot
_TYPE_TO_SLOT: dict[str, str] = {
    "aadhaar": "photo_id",
    "pan": "pan",
    "dl": "photo_id",
    "passport": "photo_id",
    "voter": "photo_id",
    "marksheet": "marksheet",
    "degree": "degree",
    "experience": "experience_letter",
    "caste": "caste_income",
    "income": "caste_income",
    "gst": "company_doc",
    "invoice": "company_doc",
    "cheque": "cancelled_cheque",
}


def slot_for_doc_type(doc_type: str) -> str:
    return _TYPE_TO_SLOT.get(doc_type, "other")


@dataclass(frozen=True)
class WorkflowStatus:
    workflow_id: str
    label: str
    present_slots: list[str]
    missing_required: list[str]
    optional_present: list[str]
    complete: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "workflow_id": self.workflow_id,
            "label": self.label,
            "present_slots": self.present_slots,
            "missing_required": self.missing_required,
            "optional_present": self.optional_present,
            "complete": self.complete,
        }


def evaluate_workflow(workflow_id: str, doc_types: list[str]) -> WorkflowStatus:
    if workflow_id not in WORKFLOWS:
        raise ValueError(f"Unknown workflow: {workflow_id}")
    spec = WORKFLOWS[workflow_id]
    slots = {slot_for_doc_type(t) for t in doc_types}
    required = list(spec["required"])  # type: ignore[arg-type]
    optional = list(spec["optional"])  # type: ignore[arg-type]
    # PAN also counts as photo_id for joining kits that only have PAN
    if "pan" in slots:
        slots.add("photo_id")
    missing = [s for s in required if s not in slots]
    opt_hit = [s for s in optional if s in slots]
    return WorkflowStatus(
        workflow_id=workflow_id,
        label=str(spec["label"]),
        present_slots=sorted(slots),
        missing_required=missing,
        optional_present=opt_hit,
        complete=len(missing) == 0,
    )
