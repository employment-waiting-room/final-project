"""Build a self-contained offline human review gallery; never runs models."""
import base64
import hashlib
import json
from pathlib import Path

from .fixtures import ROOT

RUNS = [
    "20260922T205805515147Z-e8e9aa6f", "20260922T211752221105Z-757a7092",
    "20260923T105950381566Z-9838fd29", "20260923T120515449565Z-d094ed1a",
    "20260923T123604219662Z-9ecf0176",
]


def collect(root, runs):
    rows = []
    for run in runs:
        folder = root / run
        manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
        dataset_bytes = (folder / "dataset.json").read_bytes()
        if hashlib.sha256(dataset_bytes).hexdigest() != manifest["dataset_sha256"]:
            raise ValueError(f"Dataset hash mismatch: {run}")
        fixtures = {f["id"]: f for f in json.loads(dataset_bytes)["illustrations"]}
        results = {r["attempt"]: r for r in map(json.loads, (folder / "results.jsonl").read_text().splitlines())}
        for request in manifest["schedule"]:
            attempt = request["attempt"]
            if not attempt.isalnum():
                raise ValueError("Invalid attempt ID")
            content = (folder / attempt / "image.png").read_bytes()
            sha = hashlib.sha256(content).hexdigest()
            if sha != results[attempt].get("sha256"):
                raise ValueError(f"Image hash mismatch: {run}/{attempt}")
            fixture = fixtures[request["fixture"]]
            rows.append({"id": f"{run}/{attempt}", "candidate": request["candidate"],
                         "fixture": request["fixture"], "seed": request["seed"],
                         "sha256": sha, "required": fixture["required_details"],
                         "forbidden": fixture["forbidden_details"],
                         "image": "data:image/png;base64," + base64.b64encode(content).decode()})
    if len({r["id"] for r in rows}) != len(rows):
        raise ValueError("Duplicate image IDs")
    # Compare one room/seed across candidates; original order retained within group.
    return sorted(rows, key=lambda r: (r["fixture"], r["seed"]))


def build(root=ROOT / "generated/image-evaluations", runs=RUNS,
          output=ROOT / "generated/image-review-gallery.html"):
    rows = collect(root, runs)
    identity = hashlib.sha256(json.dumps([(r["id"], r["sha256"]) for r in rows]).encode()).hexdigest()
    payload = json.dumps({"gallery_id": identity, "images": rows}).replace("<", "\\u003c")
    template = Path(__file__).with_name("image_gallery.html").read_text(encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(template.replace("__GALLERY_DATA__", payload), encoding="utf-8")
    return output


if __name__ == "__main__":
    print(f"Saved offline gallery: {build()}")
