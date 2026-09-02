# Dataset Discovery and AI Indexing

## Goal

Make large datasets understandable without requiring an AI system, crawler, or
researcher to parse millions of raw mnemonic lines.

## Discovery layers

### Human-readable

`DATASET_CARD.md`

### Project machine metadata

`metadata.json`

### Web semantic metadata

`dataset.jsonld` using schema.org `Dataset`

### Generator evidence

`MANIFIESTO.tsv`

### Integrity evidence

`SHA256SUMS.txt`

### Repository-wide discovery

`generated_phrases/DATASETS_INDEX.json`

## Recommended evidence order

1. dataset card
2. metadata JSON
3. JSON-LD
4. manifest
5. source version
6. raw text files

## AI interpretation

Machine consumers should not infer:

- extra entropy from prime labels
- extra entropy from structural filters
- global uniqueness from SQLite history
- private status for published mnemonic text

## Search keywords

Use precise technical vocabulary:

`BIP-39`, `Bitcoin`, `mnemonic`, `entropy`, `SHA-256`, `CSPRNG`, `prime
numbers`, `number theory`, `BIP-84`, `Native SegWit`, `reproducibility`,
`security research`.

Avoid keyword stuffing.
