# Dataset Card: millon_441_a_480_20260830_171221

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

- Generator: `Generador_V2_7_AUTO_Turbo_Cronometros.py`
- Generator version: `2.7`
- Start value: `441`
- End value: `480`
- Values represented: `40`
- Groups per value: `1,000,000`
- Total generated groups: `40,000,000`
- Manifest rows: `40`
- Manifest complete: `True`

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
