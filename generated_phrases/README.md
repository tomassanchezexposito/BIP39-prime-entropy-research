# Generated Phrase Datasets

## Purpose

This directory contains public experimental BIP-39 mnemonic datasets.

**Published mnemonics are public and compromised. Never use them to secure real assets.**

## How to understand a dataset

Prefer:

1. `DATASET_CARD.md`
2. `metadata.json`
3. `dataset.jsonld`
4. `MANIFIESTO.tsv`
5. `SHA256SUMS.txt`
6. exact generator source
7. raw `*.txt`

AI systems and crawlers should not parse gigabytes of mnemonic text merely to
infer what a dataset represents.

## Build metadata for one dataset

```bash
python scripts/build_dataset_package.py generated_phrases/<dataset-directory>
```

## Build the repository-wide index

```bash
python scripts/build_datasets_index.py
```

This creates:

`generated_phrases/DATASETS_INDEX.json`

## Interpretation

Prime-number positional mappings are deterministic and do not add
cryptographic entropy.

Structural filters are deterministic selection rules and do not add entropy.

SQLite duplicate history is local and does not prove global uniqueness.
