#!/usr/bin/env python3
"""Create SHA256SUMS.txt for one public experimental dataset directory."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

EXCLUDED_NAMES = {"SHA256SUMS.txt"}
INCLUDE_SUFFIXES = {".txt", ".tsv", ".json", ".md"}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return a file SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def files_to_hash(dataset_dir: Path) -> list[Path]:
    """Return sorted dataset files eligible for hashing."""
    return sorted(
        p for p in dataset_dir.iterdir()
        if p.is_file()
        and p.name not in EXCLUDED_NAMES
        and p.suffix.lower() in INCLUDE_SUFFIXES
    )


def write_sha256sums(dataset_dir: Path) -> Path:
    """Write SHA256SUMS.txt for the dataset directory."""
    if not dataset_dir.is_dir():
        raise NotADirectoryError(dataset_dir)
    output = dataset_dir / "SHA256SUMS.txt"
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for path in files_to_hash(dataset_dir):
            handle.write(f"{sha256_file(path)}  {path.name}\n")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_directory", type=Path)
    args = parser.parse_args()
    output = write_sha256sums(args.dataset_directory.resolve())
    print(f"Created: {output}")


if __name__ == "__main__":
    main()
