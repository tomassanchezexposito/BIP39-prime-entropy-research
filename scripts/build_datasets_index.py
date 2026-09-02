#!/usr/bin/env python3
"""Build generated_phrases/DATASETS_INDEX.json from dataset metadata.json files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_metadata(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    datasets_root = repo_root / "generated_phrases"
    entries: list[dict[str, Any]] = []

    for metadata_path in sorted(datasets_root.glob("*/metadata.json")):
        metadata = load_metadata(metadata_path)
        if not metadata:
            continue
        generation = metadata.get("generation", {})
        entries.append(
            {
                "dataset_id": metadata.get("dataset_id", metadata_path.parent.name),
                "path": str(metadata_path.parent.relative_to(repo_root)).replace("\\\\", "/"),
                "created_at": metadata.get("created_at"),
                "generator": metadata.get("generator"),
                "start_value": generation.get("start_value"),
                "end_value": generation.get("end_value"),
                "total_groups": generation.get("total_groups"),
                "public_test_data": metadata.get("public_test_data"),
                "metadata": str(metadata_path.relative_to(repo_root)).replace("\\\\", "/"),
            }
        )

    output = datasets_root / "DATASETS_INDEX.json"
    payload = {
        "schema_version": "1.0",
        "repository": "https://github.com/tomassanchezexposito/BIP39-prime-entropy-research",
        "dataset_count": len(entries),
        "datasets": entries,
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\\n", encoding="utf-8")
    print(f"Created: {output}")
    print(f"Datasets indexed: {len(entries)}")


if __name__ == "__main__":
    main()
