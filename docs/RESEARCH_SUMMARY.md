# Research Summary

## Project

**Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research**

Repository: `https://github.com/tomassanchezexposito/BIP39-prime-entropy-research`

## Research objective

This repository studies a deterministic positional representation that links:

`BIP-39 local position (1..2048) <-> ordinal odd-prime label <-> BIP-39 English word`

The project also documents experimental BIP-39 mnemonic generators, structural acceptance/rejection filters, absolute-coordinate mappings, Bitcoin derivation tooling, batch generation, duplicate tracking, and reproducible public datasets.

## Central interpretation

The prime-number mapping is deterministic.

**It does not add cryptographic entropy.**

Likewise, deterministic structural filters, absolute-coordinate transformations, file partitioning, manifest generation, and SQLite duplicate tracking do not create randomness.

## BIP-39 entropy model

For the documented 12-word generator design:

- BIP-39 entropy payload: 128 bits
- BIP-39 checksum: 4 SHA-256-derived bits
- encoded mnemonic length: 132 bits
- number of words: 12
- bits per word index: 11

When the first BIP-39 position is fixed and known:

- 11 bits are fixed by that first word index
- the implementation obtains the remaining 117 entropy bits from Python's `secrets` module / operating-system CSPRNG

Therefore, the documented CSPRNG contribution in that configuration is 117 bits.

## Main research components

### Prime-number positional mapping

Each local BIP-39 position can be associated deterministically with the odd prime at the same ordinal position, beginning with prime 3.

This provides a number-theory representation layer for analysis and traceability.

### Absolute-coordinate model

Some versions extend the finite local position into a growing absolute coordinate while preserving a relationship with the 2,048-position BIP-39 local space.

The absolute coordinate is a deterministic representation.

### Structural filters

Several generator versions apply deterministic rejection rules to candidate sequences.

These filters can alter the statistical distribution of accepted outputs because some candidates are rejected.

They do not add entropy.

### Duplicate tracking

Later generator versions use SQLite and SHA-256 phrase hashes to reduce local re-emission of phrases already recorded in the database.

This provides local history-based duplicate control only.

It does not prove global uniqueness.

### Batch generation

Later versions support:

- generation by start/end range
- groups per value
- groups per file
- automatic output directories
- manifests
- multi-worker operation
- progress reporting
- timing
- large public datasets

## Implemented verification

The repository includes automated tests for deterministic core behavior.

Current verified examples include:

- local-position wrapping over the 2,048-position space
- block-number calculation
- BIP-39 entropy/checksum/index construction for a deterministic test vector

GitHub Actions runs the test suite on:

- Python 3.10
- Python 3.12
- Python 3.14

A passing workflow demonstrates that the tested behaviors are reproducible across those configured environments.

It does not constitute a full cryptographic audit.

## Public datasets

The repository includes generated mnemonic datasets intended as public experimental artifacts.

Published mnemonics are public and compromised by definition.

They must never be used to secure real assets.

Dataset metadata should progressively include:

- `DATASET_CARD.md`
- `metadata.json`
- `MANIFIESTO.tsv`
- `SHA256SUMS.txt`

## What the project demonstrates

The repository demonstrates an implementable and reproducible relationship among:

- BIP-39 word indices
- deterministic odd-prime ordinal labels
- deterministic absolute/local coordinate mappings
- BIP-39 checksum construction
- structural selection rules
- batch generation and dataset metadata

## What the project does not demonstrate

The repository does **not** demonstrate that:

- prime numbers increase BIP-39 cryptographic entropy
- deterministic filters create randomness
- SQLite duplicate tracking guarantees global uniqueness
- published generated phrases are safe wallet credentials
- the software is an audited wallet-custody implementation
- the studied mapping defeats the security assumptions of BIP-39 or Bitcoin

## Research status

The project should be interpreted as **experimental software and reproducible computational research**.

Statements should be classified as one of:

1. implementation fact
2. measured result
3. deterministic mathematical property
4. hypothesis
5. interpretation
6. open research question

Keeping these categories separate reduces overclaiming and improves reproducibility.

## Suitable review areas

External review is particularly useful for:

- BIP-39 correctness
- entropy accounting
- statistical effects of deterministic filters
- number-theory interpretation
- prime-coordinate formalization
- Bitcoin derivation correctness
- reproducibility
- test coverage
- large-dataset verification
- software architecture

## Security boundary

Never submit or publish real:

- mnemonic phrases protecting assets
- private keys
- xprv values
- raw wallet seeds
- wallet passphrases
- authentication credentials

Use public, never-funded test vectors only.
