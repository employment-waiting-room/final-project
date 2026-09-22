"""Validate reserved intent fixtures offline; never invoke a model.

Run python -m observatory.held_out. The development loader intentionally rejects
this split. Final evaluation needs a separately reviewed release workflow.
"""
import hashlib
import json
import re
from pathlib import Path
from typing import Literal

from .fixtures import DATA, ROOT, Dataset, load_dataset

RESERVED = ROOT / "evaluation" / "held_out_intent.json"
MANIFEST = ROOT / "evaluation" / "held_out_intent_reservation.json"


class ReservedDataset(Dataset):
    version: Literal["world-v2-held-out-intent-v1"]
    split: Literal["held_out"]


def normalise(text):
    return " ".join(re.findall(r"\w+", text.casefold()))


def validate_separation(reserved, development):
    """Reject reused IDs/wording, including case and punctuation variations.

    Shared world states and action semantics are intentional. This check does
    not establish semantic novelty or independent human annotation.
    """
    if {c.id for c in reserved.cases} & {c.id for c in development.cases}:
        raise ValueError("Reserved and development IDs overlap")
    requests = [normalise(c.request) for c in reserved.cases]
    if len(requests) != len(set(requests)):
        raise ValueError("Duplicate reserved wording")
    if set(requests) & {normalise(c.request) for c in development.cases}:
        raise ValueError("Reserved and development wording overlaps")


def load_reserved(path=RESERVED, manifest_path=MANIFEST, development_path=DATA):
    raw = Path(path).read_bytes()
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if manifest["status"] != "reserved_not_run":
        raise ValueError("Reservation status changed; review release protocol")
    if hashlib.sha256(raw).hexdigest() != manifest["dataset_sha256"]:
        raise ValueError("Reserved dataset changed since reservation")
    dataset = ReservedDataset.model_validate_json(raw)
    if manifest["case_count"] != len(dataset.cases) or manifest["dataset_version"] != dataset.version:
        raise ValueError("Reservation metadata does not match dataset")
    validate_separation(dataset, load_dataset(development_path))
    return dataset


if __name__ == "__main__":
    reserved = load_reserved()
    print(f"Validated {len(reserved.cases)} reserved intent cases offline; no predictions generated.")
