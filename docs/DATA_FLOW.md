# Data Flow

## Purpose

This document follows one candidate from random input through dataset output.

## 1. Session input

Typical batch parameters include:

```text
start value
end value
groups per value
groups per file
destination
output prefix
worker count
```

These parameters configure the generation session.

They are not cryptographic entropy.

## 2. First-position selection

In the documented V2.7 flow, the session's absolute starting value maps deterministically to a local BIP-39 position.

Conceptually:

```text
absolute_position
    ↓
local_position 1..2048
    ↓
first_index 0..2047
```

## 3. Entropy construction

For the 12-word V2.7 design:

```text
known first index: 11 bits
CSPRNG tail:       117 bits
---------------------------
entropy payload:   128 bits
```

The random tail is generated using Python `secrets`.

## 4. BIP-39 checksum

The 128-bit entropy is converted to 16 bytes.

SHA-256 is calculated.

The first four checksum bits are appended to the entropy.

```text
128 entropy bits + 4 checksum bits = 132 bits
```

## 5. BIP-39 indexes

The 132-bit value is split into twelve 11-bit indexes.

Each index is in:

```text
0..2047
```

The corresponding user-facing local positions are:

```text
1..2048
```

## 6. Structural filter

The local-position sequence is evaluated by the generator's deterministic structural filter.

```text
candidate
   ↓
filter
 ┌─┴─┐
reject accept
  ↑      ↓
new randomness  continue
```

Important:

The filter does not add entropy.

It only rejects some candidates.

## 7. Word lookup

Accepted indexes select words from the BIP-39 English wordlist.

```text
index -> word
```

The mnemonic phrase is assembled.

## 8. Duplicate history

The phrase text is hashed using SHA-256.

The hash is inserted into SQLite using duplicate-safe persistence logic.

If the phrase hash already exists in the local database, the candidate is rejected and generation continues.

This is local history-based duplicate control.

## 9. Absolute-coordinate lifting

The local positional sequence is mapped into the project's absolute-coordinate representation.

This step is deterministic.

## 10. Batch accounting

The accepted candidate contributes to:

- current value group count
- global group count
- output file count
- manifest state
- GUI progress

## 11. TXT output

Mnemonic phrases are written to the configured output text file.

Large files may later be managed through Git LFS.

## 12. MANIFEST output

The manifest records session/file accounting such as:

- value
- part
- filename
- groups generated
- first global group
- last global group
- first absolute position
- next absolute position
- completion state

## 13. Dataset metadata

Post-processing tooling can create:

```text
DATASET_CARD.md
metadata.json
dataset.jsonld
SHA256SUMS.txt
```

## 14. Repository-wide index

`build_datasets_index.py` aggregates dataset metadata into:

```text
generated_phrases/DATASETS_INDEX.json
```

This allows machine discovery without scanning all dataset directories.

## Evidence hierarchy

For explaining what happened in a generation session:

```text
source version
    +
manifest
    +
dataset metadata
    +
hashes
    +
tests
```

are stronger evidence than inference from raw phrase text alone.
