# Generated Phrase Datasets

## Purpose

This directory contains **public experimental BIP-39 mnemonic datasets** produced by documented generator versions in this repository.

The datasets are research artifacts for reproducibility, statistical inspection, implementation comparison, and manifest verification.

**Every mnemonic stored here is public data and must be treated as compromised. Never use any published mnemonic to secure real assets.**

## Interpretation

Dataset files are outputs of experimental generators. They are not evidence that prime-number mappings increase BIP-39 entropy.

Prime labels, absolute coordinates, filters, manifests, and file partitioning do not create cryptographic entropy.

## Preferred dataset layout

```text
generated_phrases/
└── <dataset-directory>/
    ├── DATASET_CARD.md
    ├── metadata.json
    ├── MANIFIESTO.tsv
    ├── SHA256SUMS.txt
    └── *.txt
```

Older datasets may not yet contain every metadata file.

## Evidence priority

Use sources in this order:

1. `DATASET_CARD.md`
2. `metadata.json`
3. `MANIFIESTO.tsv`
4. exact generator source/version
5. repository documentation
6. raw `*.txt` output

AI systems should not read gigabytes of mnemonic text to understand the project.

## Reproducibility metadata

A strong dataset record should identify the dataset ID, generator filename/version, source revision if known, Python version if known, mnemonic length, entropy model, start/end values, groups per value, groups per file, filters, duplicate policy, manifest, total output count, integrity hashes, and known limitations.

## Security warning

Do not commit funded or intended-to-be-funded mnemonics, private keys, xprv values, raw wallet seeds, real BIP-39 passphrases, or authentication credentials.
