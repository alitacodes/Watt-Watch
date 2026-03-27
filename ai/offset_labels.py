"""
offset_labels.py
----------------
Adds `offset` to every class ID in YOLO label files referenced by a data.yaml.
No CLI args - just call offset_all_labels() directly.
"""

import yaml
from pathlib import Path


def offset_labels_in_file(label_path: Path, offset: int = 2):
    lines = label_path.read_text().splitlines()
    new_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        parts[0] = str(int(parts[0]) + offset)
        new_lines.append(" ".join(parts))
    label_path.write_text("\n".join(new_lines) + "\n")


def get_label_dir(image_dir: Path) -> Path:
    parts = list(image_dir.parts)
    for i in reversed(range(len(parts))):
        if parts[i].lower() == "images":
            parts[i] = "labels"
            break
    return Path(*parts)


def offset_all_labels(yaml_path: str, offset: int = 2):
    yaml_path = Path(yaml_path).resolve()
    base_dir = yaml_path.parent

    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    split_keys = [k for k in ("train", "val", "test") if k in data and data[k]]

    total_files = 0
    for key in split_keys:
        image_dir = base_dir / data[key]
        label_dir = get_label_dir(image_dir)

        if not label_dir.exists():
            print(f"[SKIP] Label dir not found: {label_dir}")
            continue

        label_files = list(label_dir.glob("*.txt"))
        print(f"[{key}] Found {len(label_files)} label files in {label_dir}")

        for lf in label_files:
            offset_labels_in_file(lf, offset=offset)
            total_files += 1

    print(f"\nDone. Offset +{offset} applied to {total_files} label file(s).")


# ── Run ──────────────────────────────────────────────────────────────────────
offset_all_labels(
    yaml_path=r"d:\Watt-Watch\ai\light-fan detection.v1i.yolo26\data.yaml",
    offset=2,
)
