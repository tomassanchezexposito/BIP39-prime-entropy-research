#!/usr/bin/env python3
"""Build machine-readable metadata for one public experimental dataset folder.

The script reads MANIFIESTO.tsv when present, inventories dataset files, computes
SHA-256 hashes, and writes:
- DATASET_CARD.md
- metadata.json
- dataset.jsonld
- SHA256SUMS.txt

It never generates mnemonics, derives keys, or inspects wallet balances.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
from datetime import datetime
from pathlib import Path
from typing import Any

REPOSITORY_URL = "https://github.com/tomassanchezexposito/BIP39-prime-entropy-research"
DEFAULT_GENERATOR = "Generador_V2_7_AUTO_Turbo_Cronometros.py"
DEFAULT_GENERATOR_VERSION = "2.7"
HASH_CHUNK_SIZE = 1024 * 1024
PUBLIC_SUFFIXES = {".txt", ".tsv", ".json", ".md"}
GENERATED_METADATA_NAMES = {
    "DATASET_CARD.md",
    "metadata.json",
    "dataset.jsonld",
    "SHA256SUMS.txt",
}

EXPECTED_MANIFEST_COLUMNS = {
    "valor",
    "parte",
    "archivo",
    "grupos_generados",
    "primer_grupo_global",
    "ultimo_grupo_global",
    "primera_posicion_absoluta",
    "siguiente_posicion_absoluta",
    "estado",
}


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(HASH_CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


def parse_directory_timestamp(name: str) -> str | None:
    """Infer an ISO timestamp from a trailing YYYYMMDD_HHMMSS directory name."""
    match = re.search(r"_(\d{8})_(\d{6})$", name)
    if not match:
        return None
    try:
        dt = datetime.strptime("".join(match.groups()), "%Y%m%d%H%M%S")
    except ValueError:
        return None
    return dt.isoformat(timespec="seconds")


def read_manifest(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 TSV manifest into normalized dictionaries."""
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        rows = []
        for raw in reader:
            row = {
                (key or "").strip(): (value or "").strip()
                for key, value in raw.items()
            }
            if any(row.values()):
                rows.append(row)
        return rows


def as_int(value: str | None) -> int | None:
    """Parse an integer field, returning None for blank/non-integer values."""
    if value is None:
        return None
    value = value.strip().replace(",", "")
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def manifest_summary(rows: list[dict[str, str]]) -> dict[str, Any]:
    """Summarize the documented V2.7-style manifest without inventing values."""
    if not rows:
        return {
            "row_count": 0,
            "columns_recognized": False,
            "start_value": None,
            "end_value": None,
            "value_count": None,
            "groups_per_value": None,
            "groups_per_file": None,
            "total_groups": None,
            "first_global_group": None,
            "last_global_group": None,
            "output_file_count": None,
            "all_rows_complete": None,
        }

    columns = set(rows[0])
    recognized = EXPECTED_MANIFEST_COLUMNS.issubset(columns)

    values = [as_int(r.get("valor")) for r in rows]
    values = [v for v in values if v is not None]
    groups = [as_int(r.get("grupos_generados")) for r in rows]
    groups = [g for g in groups if g is not None]
    first_globals = [as_int(r.get("primer_grupo_global")) for r in rows]
    first_globals = [v for v in first_globals if v is not None]
    last_globals = [as_int(r.get("ultimo_grupo_global")) for r in rows]
    last_globals = [v for v in last_globals if v is not None]
    files = [r.get("archivo", "").strip() for r in rows if r.get("archivo", "").strip()]
    states = [r.get("estado", "").strip().upper() for r in rows if r.get("estado", "").strip()]

    unique_groups = sorted(set(groups))
    groups_per_value = unique_groups[0] if len(unique_groups) == 1 else None

    # In the current generator family one manifest row normally maps to one output part.
    groups_per_file = groups_per_value

    return {
        "row_count": len(rows),
        "columns_recognized": recognized,
        "start_value": min(values) if values else None,
        "end_value": max(values) if values else None,
        "value_count": len(set(values)) if values else None,
        "groups_per_value": groups_per_value,
        "groups_per_file": groups_per_file,
        "total_groups": sum(groups) if groups else None,
        "first_global_group": min(first_globals) if first_globals else None,
        "last_global_group": max(last_globals) if last_globals else None,
        "output_file_count": len(set(files)) if files else None,
        "all_rows_complete": all(s == "COMPLETO" for s in states) if states else None,
    }


def inventory_files(dataset_dir: Path) -> list[dict[str, Any]]:
    """Return a deterministic inventory of public dataset files."""
    entries: list[dict[str, Any]] = []
    for path in sorted(dataset_dir.iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file():
            continue
        if path.name in GENERATED_METADATA_NAMES:
            continue
        if path.suffix.lower() not in PUBLIC_SUFFIXES:
            continue
        entries.append(
            {
                "name": path.name,
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return entries


def write_sha256sums(dataset_dir: Path, inventory: list[dict[str, Any]]) -> None:
    """Write hashes for original dataset files plus generated metadata files."""
    candidates = {
        item["name"]: item["sha256"]
        for item in inventory
    }

    for name in ("DATASET_CARD.md", "metadata.json", "dataset.jsonld"):
        path = dataset_dir / name
        if path.exists():
            candidates[name] = sha256_file(path)

    output = dataset_dir / "SHA256SUMS.txt"
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for name in sorted(candidates, key=str.lower):
            handle.write(f"{candidates[name]}  {name}\n")


def build_metadata(
    dataset_dir: Path,
    summary: dict[str, Any],
    inventory: list[dict[str, Any]],
    generator: str,
    generator_version: str,
    git_commit: str | None,
) -> dict[str, Any]:
    """Build project-specific machine-readable metadata."""
    dataset_id = dataset_dir.name
    txt_files = [f for f in inventory if f["name"].lower().endswith(".txt")]
    total_bytes = sum(f["size_bytes"] for f in inventory)

    return {
        "schema_version": "1.1",
        "dataset_id": dataset_id,
        "dataset_type": "experimental_bip39_mnemonics",
        "description": "Public experimental BIP-39 mnemonic dataset for reproducibility and research.",
        "public_test_data": True,
        "created_at": parse_directory_timestamp(dataset_id),
        "repository": REPOSITORY_URL,
        "git_commit": git_commit,
        "environment": {
            "metadata_builder_python": platform.python_version(),
            "platform": platform.system(),
        },
        "generator": {
            "filename": generator,
            "version": generator_version,
        },
        "mnemonic": {
            "word_count": 12,
            "language": "english",
        },
        "entropy_model": {
            "source": "python-secrets / operating-system CSPRNG",
            "entropy_bits": 128,
            "fixed_known_bits": 11,
            "csprng_bits": 117,
            "checksum_bits": 4,
            "notes": (
                "Applies to the documented V2.7 design when the first BIP-39 "
                "position is fixed and known."
            ),
        },
        "prime_mapping_adds_entropy": False,
        "structural_filters_add_entropy": False,
        "duplicate_policy": {
            "method": "SQLite SHA-256 phrase hashes",
            "scope": "local database history",
            "global_uniqueness_claimed": False,
        },
        "generation": summary,
        "files": {
            "inventory_count": len(inventory),
            "mnemonic_txt_file_count": len(txt_files),
            "total_inventory_bytes": total_bytes,
            "manifest_file": "MANIFIESTO.tsv" if (dataset_dir / "MANIFIESTO.tsv").exists() else None,
            "hash_file": "SHA256SUMS.txt",
            "dataset_card": "DATASET_CARD.md",
            "schema_org_jsonld": "dataset.jsonld",
        },
        "security_warning": (
            "Public experimental data. Never use published mnemonics to secure real assets."
        ),
    }


def build_jsonld(metadata: dict[str, Any]) -> dict[str, Any]:
    """Build schema.org Dataset JSON-LD for discovery/indexing."""
    generation = metadata["generation"]
    dataset_id = metadata["dataset_id"]

    description = metadata["description"]
    if generation.get("start_value") is not None and generation.get("end_value") is not None:
        description += (
            f" Generator-value range {generation['start_value']}..{generation['end_value']}."
        )
    if generation.get("total_groups") is not None:
        description += f" Manifested generated groups: {generation['total_groups']}."

    return {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"BIP39 Prime Entropy Research Dataset — {dataset_id}",
        "description": description,
        "url": f"{REPOSITORY_URL}/tree/main/generated_phrases/{dataset_id}",
        "isBasedOn": REPOSITORY_URL,
        "creator": {
            "@type": "Person",
            "name": "Tomas Sanchez Exposito",
            "url": "https://github.com/tomassanchezexposito",
        },
        "inLanguage": "en",
        "keywords": [
            "BIP-39",
            "Bitcoin",
            "mnemonic",
            "entropy",
            "cryptography",
            "prime numbers",
            "number theory",
            "security research",
            "reproducibility",
        ],
        "dateCreated": metadata.get("created_at"),
        "encodingFormat": ["text/plain", "text/tab-separated-values", "application/json"],
        "conditionsOfAccess": (
            "Public research data. Published mnemonics must never be used to secure assets."
        ),
        "measurementTechnique": (
            "Experimental Python BIP-39 generation with deterministic prime-position "
            "representation and documented structural filtering."
        ),
        "variableMeasured": [
            "BIP-39 mnemonic output",
            "generator value",
            "global group index",
            "absolute positional metadata",
        ],
    }


def build_card(metadata: dict[str, Any]) -> str:
    """Render a concise human/AI-readable dataset card."""
    g = metadata["generation"]
    dataset_id = metadata["dataset_id"]

    def value(key: str) -> str:
        result = g.get(key)
        return "unknown" if result is None else f"{result:,}"

    return f"""# Dataset Card: {dataset_id}

## Summary

Public experimental **12-word BIP-39 mnemonic dataset** produced for reproducibility,
statistical inspection, and implementation research.

**Security classification:** public test data. Never use a published mnemonic to
secure real funds.

## Machine-readable metadata

- `metadata.json` — project-specific metadata
- `dataset.jsonld` — schema.org `Dataset` JSON-LD
- `MANIFIESTO.tsv` — generator session manifest, when present
- `SHA256SUMS.txt` — SHA-256 file-integrity digests

## Generation

- Generator: `{metadata["generator"]["filename"]}`
- Generator version: `{metadata["generator"]["version"]}`
- Start value: `{value("start_value")}`
- End value: `{value("end_value")}`
- Values represented: `{value("value_count")}`
- Groups per value: `{value("groups_per_value")}`
- Total generated groups: `{value("total_groups")}`
- Manifest rows: `{value("row_count")}`
- Manifest complete: `{g.get("all_rows_complete")}`

## Entropy interpretation

For the documented V2.7 12-word design with a fixed known first BIP-39 position:

- BIP-39 entropy payload: 128 bits
- fixed known first-index contribution: 11 bits
- CSPRNG-generated remainder: 117 bits
- checksum: 4 SHA-256-derived bits
- random source: Python `secrets` / operating-system CSPRNG

**Prime-number mappings do not add cryptographic entropy.**

**Structural filters do not add cryptographic entropy.**

## Duplicate interpretation

SQLite SHA-256 phrase-hash tracking reduces local re-emission relative to the
database history available to that installation. It does not establish global
uniqueness and does not add entropy.

## Responsible use

Use this dataset for research, reproducibility, software testing, metadata
inspection, and statistical analysis.

Do not use any published mnemonic as a wallet credential.

## Verification

Verify file integrity using `SHA256SUMS.txt` and interpret the dataset through
`metadata.json`, `dataset.jsonld`, and `MANIFIESTO.tsv` before processing the raw
mnemonic files.
"""


def get_git_commit(repo_root: Path) -> str | None:
    """Return HEAD commit if available without failing metadata creation."""
    head = repo_root / ".git" / "HEAD"
    if not head.exists():
        return None
    try:
        text = head.read_text(encoding="utf-8").strip()
        if text.startswith("ref: "):
            ref = repo_root / ".git" / text[5:]
            return ref.read_text(encoding="utf-8").strip() if ref.exists() else None
        return text or None
    except OSError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build metadata and integrity files for one public dataset directory."
    )
    parser.add_argument("dataset_directory", type=Path)
    parser.add_argument("--generator", default=DEFAULT_GENERATOR)
    parser.add_argument("--generator-version", default=DEFAULT_GENERATOR_VERSION)
    args = parser.parse_args()

    dataset_dir = args.dataset_directory.resolve()
    if not dataset_dir.is_dir():
        raise NotADirectoryError(dataset_dir)

    rows = read_manifest(dataset_dir / "MANIFIESTO.tsv")
    summary = manifest_summary(rows)
    inventory = inventory_files(dataset_dir)

    repo_root = Path(__file__).resolve().parents[1]
    metadata = build_metadata(
        dataset_dir,
        summary,
        inventory,
        args.generator,
        args.generator_version,
        get_git_commit(repo_root),
    )

    (dataset_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (dataset_dir / "dataset.jsonld").write_text(
        json.dumps(build_jsonld(metadata), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (dataset_dir / "DATASET_CARD.md").write_text(
        build_card(metadata),
        encoding="utf-8",
    )

    # Regenerate hashes after all generated metadata exists.
    write_sha256sums(dataset_dir, inventory)

    print(f"Dataset metadata created: {dataset_dir}")
    print(f"Manifest rows: {summary['row_count']}")
    print(f"Total groups: {summary['total_groups']}")
    print(f"Inventory files: {len(inventory)}")


if __name__ == "__main__":
    main()
