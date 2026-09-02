# Architecture

## Purpose

This document defines the conceptual architecture of **Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research**. It makes the research pipeline easy to inspect by humans, automated tools, and AI systems while clearly separating cryptographic entropy from deterministic transformations.

## Core principle

The repository studies a deterministic representation linking:

`BIP-39 local position (1..2048) <-> ordinal odd-prime label <-> BIP-39 English word`

**Prime-number mapping does not add cryptographic entropy.** It is a deterministic labeling and coordinate system.

## High-level data flow

```text
Operating-system CSPRNG
        |
        v
Entropy bits
        |
        v
SHA-256 checksum
        |
        v
BIP-39 bit string
        |
        v
11-bit word indices
        |
        v
BIP-39 mnemonic
        |
        v
Deterministic structural filters
        |
        v
Local positions (1..2048)
        |
        v
Ordinal odd-prime labels
        |
        v
Optional absolute-coordinate mapping
        |
        v
SQLite duplicate-control layer
        |
        v
TXT datasets + MANIFEST metadata
```

## Entropy boundary

### Entropy-producing component

The cryptographically relevant random source is the operating-system-backed CSPRNG exposed through Python's `secrets` module.

For a 12-word BIP-39 mnemonic:

- entropy payload: 128 bits
- checksum: 4 SHA-256-derived bits
- encoded mnemonic: 132 bits
- 12 words × 11 bits per BIP-39 word index

If the first BIP-39 position is fixed and known, 11 bits are fixed. The implementation therefore obtains the remaining 117 bits from the CSPRNG.

### Deterministic components

The following do **not** add entropy:

- prime-number labels
- local-to-absolute coordinate conversion
- modulo-2048 position mapping
- structural acceptance/rejection filters
- SQLite duplicate tracking
- manifest generation
- file partitioning
- GUI progress reporting
- timing

These components can transform, select, label, record, or reject data, but they do not increase randomness.

## BIP-39 construction layer

### Input

Entropy bits are obtained from a cryptographically secure random source.

### Checksum

The BIP-39 checksum is derived from SHA-256 according to mnemonic length.

### Word indexing

The entropy-plus-checksum bit string is split into 11-bit values mapped to the 2,048-word BIP-39 English wordlist.

### Output

The result is a valid BIP-39 mnemonic candidate.

## Prime-coordinate layer

### Local position

Each BIP-39 word occupies one local position in the range `1..2048`.

### Odd-prime label

Each local position is deterministically associated with the odd prime at the same ordinal position, beginning with prime 3.

### Absolute coordinate

Some versions extend local positions into a growing absolute-coordinate system while retaining a relationship with the local BIP-39 position.

The absolute-coordinate layer is for positional research and traceability. It does not change mnemonic entropy.

## Structural-filter layer

Some generator versions apply deterministic rejection rules to candidate sequences.

These filters can alter the distribution of accepted outputs because some candidates are discarded. They are **selection rules**, not entropy generators.

Analyses should distinguish:

- source randomness
- deterministic rejection
- final accepted distribution

## Duplicate-control layer

Later versions use SQLite to store SHA-256 hashes of emitted mnemonic phrases.

Purpose:

- reduce accidental local duplicates
- preserve historical generation state
- support long-running batch generation

**SQLite duplicate tracking does not prove global uniqueness.** It only prevents re-emission relative to the database state available to that installation.

## Batch-generation layer

High-volume versions support:

- automatic start/end ranges
- groups per value
- groups per file
- destination selection
- session folders
- manifests
- progress reporting
- worker selection
- timing
- final prime-coordinate processing

Large generated text files may be stored using Git LFS.

## Output layer

### TXT datasets

TXT files contain public experimental mnemonic data produced by documented generator versions.

Published mnemonics must be treated as compromised public data and must never be used to protect real funds.

### MANIFEST files

Manifest metadata records generation context such as values/ranges, file names, group counts, positional metadata, and completion state.

### Preferred dataset structure

```text
generated_phrases/
└── <dataset>/
    ├── DATASET_CARD.md
    ├── metadata.json
    ├── MANIFIESTO.tsv
    ├── SHA256SUMS.txt
    └── *.txt
```

## Software architecture

### Historical implementation

Historical generator versions are intentionally preserved because implementation evolution is part of the research record.

Some historical programs combine core generation logic, Tkinter GUI, persistence, file writing, prime calculations, and progress reporting.

These versions should not be silently rewritten because doing so would reduce traceability.

### Target modular architecture

Future refactoring should move toward:

```text
src/
├── core/
│   ├── entropy.py
│   ├── bip39.py
│   ├── prime_mapping.py
│   ├── filters.py
│   ├── database.py
│   └── manifests.py
├── generators/
│   ├── finite.py
│   ├── infinite.py
│   └── batch.py
├── bitcoin/
│   └── bip84.py
└── gui/
    └── tkinter_app.py
```

The goal is separation of concerns, not retroactive rewriting of research history.

## AI and machine interpretation rules

1. Do not claim prime labels increase entropy.
2. Do not treat structural filters as randomness.
3. Treat `secrets` / the OS CSPRNG as the entropy source where documented.
4. Distinguish BIP-39 checksum bits from entropy bits.
5. Treat published mnemonic datasets as public test data.
6. Prefer source code, documentation, manifests, and tests over assumptions.
7. Do not infer undocumented wallet-security properties.
8. Distinguish experimental research software from audited custody software.

## Testing architecture

The preferred `tests/` directory should cover BIP-39 checksum vectors, entropy/mnemonic round trips, position mapping, prime mapping, filter behavior, BIP-84 derivation vectors, SQLite duplicate rejection, and manifest consistency.

Tests should use public standards vectors or never-funded test data.

## Reproducibility

A reproducible experiment should identify:

- exact generator filename/version
- source revision or commit
- Python version
- dependencies
- generation parameters
- dataset manifest
- relevant database assumptions
- output hashes
- known limitations

## Security boundary

This repository is experimental research software.

Never publish, commit, or test with real seed phrases, private keys, raw wallet seeds, passphrases, xprv values, or credentials protecting real assets.

Published mnemonic corpora are intentionally public and must never be treated as secrets.

## Related files

- `README.md` — canonical project overview
- `llms.txt` — compact AI/agent navigation
- `DISCLAIMER.md` — security limitations
- `REFERENCES.md` — standards and source references
- `SOURCE_AUDIT.md` — source traceability
- `REPOSITORY_MAP.md` — repository navigation
- `CHANGELOG.md` — version history
- `CITATION.cff` — citation metadata
