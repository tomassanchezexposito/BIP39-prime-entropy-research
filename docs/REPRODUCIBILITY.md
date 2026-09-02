# Reproducibility Guide

## Purpose

This document defines a reproducible workflow for testing and reviewing results in this repository.

A reproducible result should identify the exact code, environment, parameters, and verification artifacts used.

## Minimum reproducibility record

Record at least:

- repository URL
- Git commit SHA or release tag
- exact source filename
- generator version
- operating system
- Python version
- relevant Python dependencies
- input parameters
- output directory
- manifest filename
- output file count
- generated group count
- integrity hashes
- known limitations

## Repository checkout

Clone or download the repository and record the exact commit:

```bash
git rev-parse HEAD
```

Record the result in the experiment notes.

## Python environment

Display the Python version:

```bash
python --version
```

Install the test dependency if needed:

```bash
python -m pip install pytest
```

## Automated tests

From the repository root:

```bash
python -m pytest
```

A successful local run should report all collected tests as passed.

The repository also uses GitHub Actions to run the test suite on multiple Python versions.

## What automated tests prove

A passing test demonstrates that a specific documented behavior produced the expected result under the tested environment.

It does not prove:

- complete absence of bugs
- wallet security
- cryptographic soundness beyond the tested property
- global dataset uniqueness
- increased entropy from prime mapping

## Reproducing BIP-39 core behavior

For deterministic functions, prefer fixed inputs.

Examples of suitable reproducibility targets:

- known entropy -> checksum
- known entropy -> BIP-39 indices
- absolute position -> local position
- absolute position -> block number
- known public mnemonic -> public Bitcoin address

Avoid using private or funded credentials.

## Reproducing generator behavior

Because mnemonic generation uses a CSPRNG, exact phrase-by-phrase reproduction is not normally expected unless the random source is replaced by a controlled test fixture.

Instead, reproduce invariant behavior such as:

- valid BIP-39 checksum construction
- fixed first-position constraint
- correct word count
- correct positional mapping
- filter acceptance/rejection behavior
- manifest accounting
- duplicate-control behavior

## Recording generation parameters

For a batch-generation experiment record:

```text
generator:
start_value:
end_value:
groups_per_value:
groups_per_file:
destination:
worker_count:
filter_version:
database_state:
date/time:
git_commit:
python_version:
```

## SQLite state

Later generator versions may depend on a persistent SQLite history of SHA-256 phrase hashes.

For reproducibility, state whether the database was:

- existing historical database
- new empty database
- copied snapshot
- reset database

The database affects duplicate rejection history.

Do not claim two runs are equivalent if their duplicate-history state differs.

## Dataset verification

For a machine-readable dataset directory, prefer:

```text
DATASET_CARD.md
metadata.json
MANIFIESTO.tsv
SHA256SUMS.txt
*.txt
```

## Integrity verification

Generate SHA-256 hashes with:

```bash
python scripts/generate_sha256s.py generated_phrases/<dataset-directory>
```

A hash match verifies byte identity only.

## Manifest verification

Check:

- expected number of rows
- start/end values
- groups per value
- groups per file
- first/last global group
- continuity of global-group numbering
- completion state
- output filenames

## Large datasets

Do not require an AI system or reviewer to read millions of mnemonic lines to understand a dataset.

Use metadata, manifests, hashes, and sample-based validation.

For full-file count checks, use command-line tools appropriate to the environment.

## Reproducibility levels

### Level 1 — Documentation reproducibility

A reader can understand the algorithm and parameters from documentation.

### Level 2 — Functional reproducibility

Deterministic unit tests pass and reproduce documented transformations.

### Level 3 — Session reproducibility

A generation session has recorded parameters, manifest, source revision, and environment.

### Level 4 — Dataset reproducibility

The published dataset includes machine-readable metadata and integrity hashes.

### Level 5 — Independent replication

A third party independently reproduces the documented behavior and reports the result.

## Reporting independent replication

Use the GitHub `Reproducibility report` issue form.

Include:

- commit/release
- exact source version
- environment
- parameters
- observed result
- comparison with documented behavior
- public verification artifacts

## Security

Never use reproducibility workflows with credentials protecting real assets.

Published examples must be public and never-funded.
