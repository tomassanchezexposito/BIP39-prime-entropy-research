# Hugging Face Publishing Guide

## Status

This repository is prepared to produce dataset cards and machine-readable
metadata, but publication to Hugging Face should be treated as a separate
release step.

## Important license constraint

The project currently has no selected reuse license.

Hugging Face dataset-card metadata supports a `license` field, but this project
must not invent or imply a license that has not been chosen.

Before public dataset mirroring, decide deliberately whether and how the data
and software may be reused.

## Dataset card

Hugging Face renders a dataset repository's `README.md` as the dataset card.
The YAML metadata header can define language, tags, license, and other
discoverability fields.

Use `docs/HUGGINGFACE_DATASET_CARD_TEMPLATE.md` as the starting point.

## Recommended publication unit

Do not begin by uploading every historical dataset.

Start with one well-documented dataset containing:

```text
README.md
DATASET_CARD.md
metadata.json
dataset.jsonld
MANIFIESTO.tsv
SHA256SUMS.txt
*.txt
```

## Large files

The current GitHub repository uses Git LFS for large text data. Hugging Face
also has its own storage and repository rules. Verify current Hub limits before
mirroring large corpora.

## Responsible-use statement

Every Hub dataset card should state that published BIP-39 mnemonics are public
test data and must never be used to secure assets.
