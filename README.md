# BIP39 Prime Entropy Research

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22257814.svg)](https://doi.org/10.5281/zenodo.22257814)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Experimental Python research on **BIP-39 mnemonic generation, cryptographic entropy accounting, SHA-256 checksum construction, deterministic prime-number positional mappings, absolute coordinates, structural filters, Bitcoin HD-wallet derivation, Native SegWit (BIP-84), reproducible datasets, and large-scale generation tooling**.

> **Critical interpretation:** prime-number mappings, absolute-coordinate transforms, structural filters, SQLite duplicate tracking, manifests, and file partitioning are deterministic mechanisms. They **do not add cryptographic entropy**.

## Archived research release

The citable archived software release is:

**Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research — v1.1.0**

DOI: **10.5281/zenodo.22257814**

Citation metadata is available in [`CITATION.cff`](CITATION.cff).

## Project purpose

This repository investigates a representation in which the BIP-39 English word space is associated with ordinal odd-prime labels:

```text
BIP-39 index 0..2047
        ↕
local position 1..2048
        ↕
ordinal odd-prime label
        ↕
BIP-39 English word
```

Some implementations extend this local representation into an absolute-coordinate system and apply deterministic structural filters. The repository also contains experimental generators, Bitcoin address derivation utilities, tests, manifests, public generated datasets, integrity hashes, and machine-readable metadata.

## Research questions

The repository is designed to support investigation of:

- BIP-39 entropy and checksum construction
- deterministic prime-position representations
- absolute/local coordinate mappings
- statistical effects of deterministic rejection filters
- reproducibility of large generation sessions
- SQLite-based local duplicate history
- Bitcoin BIP-32/BIP-84 derivation workflows
- machine-readable research datasets

## Entropy model

For the documented V2.7 12-word design with a fixed and known first BIP-39 position:

```text
BIP-39 entropy payload     128 bits
fixed first word index      11 bits
CSPRNG-generated remainder 117 bits
BIP-39 checksum               4 bits
encoded mnemonic            132 bits
```

The 117-bit remainder is obtained from Python's cryptographically secure `secrets` interface / operating-system CSPRNG.

The four checksum bits are SHA-256-derived and deterministic.

## What this repository does not claim

This project does **not** claim that:

- prime numbers increase BIP-39 entropy
- deterministic filters create randomness
- an absolute coordinate creates additional cryptographic security
- SQLite duplicate tracking establishes global uniqueness
- published mnemonic datasets are safe wallet credentials
- experimental research code is audited custody software
- the mapping defeats BIP-39 or Bitcoin security assumptions

## Repository navigation

### Start here

- [`llms.txt`](llms.txt) — compact navigation for AI systems and agents
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — conceptual architecture
- [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) — repository navigation
- [`docs/RESEARCH_SUMMARY.md`](docs/RESEARCH_SUMMARY.md) — research scope and claims
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) — reproduction protocol
- [`docs/VERSION_MATRIX.md`](docs/VERSION_MATRIX.md) — historical implementation map

### Technical architecture

- [`docs/TECHNICAL_ARCHITECTURE.md`](docs/TECHNICAL_ARCHITECTURE.md)
- [`docs/MODULE_MAP.md`](docs/MODULE_MAP.md)
- [`docs/DATA_FLOW.md`](docs/DATA_FLOW.md)
- [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md)
- [`docs/BIP39_PIPELINE.md`](docs/BIP39_PIPELINE.md)
- [`docs/PRIME_COORDINATE_MODEL.md`](docs/PRIME_COORDINATE_MODEL.md)
- [`docs/SQLITE_MODEL.md`](docs/SQLITE_MODEL.md)
- [`docs/AI_CODE_READING_GUIDE.md`](docs/AI_CODE_READING_GUIDE.md)

### Security and quality

- [`DISCLAIMER.md`](DISCLAIMER.md)
- [`docs/SECURITY_MODEL.md`](docs/SECURITY_MODEL.md)
- [`docs/CODE_QUALITY.md`](docs/CODE_QUALITY.md)
- [`docs/GLOSSARY.md`](docs/GLOSSARY.md)
- [`CONTRIBUTING.md`](CONTRIBUTING.md)

### Datasets

- [`generated_phrases/README.md`](generated_phrases/README.md)
- [`generated_phrases/DATASETS_INDEX.json`](generated_phrases/DATASETS_INDEX.json)
- [`docs/DATASET_DISCOVERY.md`](docs/DATASET_DISCOVERY.md)
- [`docs/dataset_metadata.schema.json`](docs/dataset_metadata.schema.json)

Machine-readable dataset packages can contain:

```text
DATASET_CARD.md
metadata.json
dataset.jsonld
MANIFIESTO.tsv
SHA256SUMS.txt
*.txt
```

## Source code

Historical implementations are preserved under [`src/`](src/).

They are part of the research record. Do not assume that every historical file represents the current recommended architecture.

For semantic navigation, read [`docs/MODULE_MAP.md`](docs/MODULE_MAP.md) before analyzing individual source files.

## Tests and continuous integration

Run:

```bash
python -m pytest
```

GitHub Actions executes the test suite on multiple Python versions.

A passing test suite is evidence for the tested deterministic behaviors; it is **not** a complete cryptographic audit.

## Dataset tooling

Build machine-readable metadata for one dataset:

```bash
python scripts/build_dataset_package.py generated_phrases/<dataset-directory>
```

Build the repository-wide dataset index:

```bash
python scripts/build_datasets_index.py
```

## Reproducibility

A reproducible experiment should record at minimum:

- exact Git commit or release
- exact source filename/version
- Python version
- operating system
- generation parameters
- structural-filter version
- SQLite history state
- manifest
- integrity hashes

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).

## Responsible use

Published mnemonic phrases are **public test data** and are compromised by definition.

Never use a mnemonic from this repository to secure real Bitcoin, cryptocurrency, tokens, or other assets.

Never submit real:

- mnemonic phrases
- private keys
- xprv values
- raw wallet seeds
- wallet passphrases
- API credentials

## Citation

If you use this software in research, cite the archived Zenodo release:

**Sánchez Exposito, T. (2026). Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research (Version v1.1.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.22257814**

See [`CITATION.cff`](CITATION.cff) for machine-readable citation metadata.

## License

The software and associated repository documentation are released under the **MIT License**. See [`LICENSE`](LICENSE).

Public generated mnemonic datasets remain public experimental material and must never be used as wallet secrets.

## Keywords

BIP-39, Bitcoin, mnemonic, seed phrase, entropy, CSPRNG, SHA-256, cryptography, prime numbers, number theory, HD wallet, BIP-32, BIP-84, Native SegWit, Bech32, secp256k1, reproducibility, security research, Python, dataset metadata.
