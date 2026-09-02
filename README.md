# Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research

> Experimental Python research on **BIP-39 mnemonic generation, entropy construction, SHA-256 checksum validation, prime-number positional mappings, Bitcoin HD-wallet derivation, Native SegWit (BIP-84), and large-scale reproducible mnemonic datasets**.

## Project purpose

This repository investigates a deterministic mapping between the 2,048-element **BIP-39 English word index**, ordinal **odd-prime positions**, and an arithmetic coordinate for odd integers. It contains Python implementations for generating and analysing BIP-39 mnemonics, applying structural filters, mapping local positions to prime-number labels, deriving Bitcoin addresses, exporting reproducible datasets, and recording implementation history.

`local BIP-39 position (1..2048) <-> odd-prime ordinal label <-> BIP-39 English word`

### Critical cryptographic interpretation

**Prime-number mapping does not add cryptographic entropy.** It is deterministic labeling.

For a 12-word BIP-39 mnemonic:
- entropy payload: **128 bits**
- checksum: **4 SHA-256-derived bits**
- encoded mnemonic: **132 bits = 12 × 11 bits**
- if the first BIP-39 position is fixed and known, 11 bits are fixed
- the implementation obtains the remaining **117 bits** from Python's cryptographically secure `secrets` module

Absolute prime coordinates and deterministic structural rejection filters do not add entropy.

## Research scope

### Prime-number positional representation
The project studies a representation of BIP-39's 2,048-word index space through ordinal odd-prime positions and an extendable absolute-coordinate model.

### BIP-39 construction
Generators construct valid 12-word and 24-word BIP-39 mnemonics while preserving traceability among entropy, checksum, indices, words, and positional labels.

### Structural filtering
Several versions test deterministic rejection rules. These alter the accepted output distribution but **do not create randomness**.

### Large-scale reproducibility
Later versions support batched generation, manifests, SQLite SHA-256 duplicate tracking, automatic ranges, file-level progress, and large experimental datasets.

## Repository structure

```text
/
├── README.md
├── llms.txt
├── CITATION.cff
├── DISCLAIMER.md
├── CHANGELOG.md
├── REFERENCES.md
├── REPOSITORY_MAP.md
├── SOURCE_AUDIT.md
├── REPOSITORY_AUDIT.json
├── src/                 # Python research implementations
├── tests/               # Automated tests/test vectors (recommended)
├── docs/                # Technical manuscript and implementation notes
├── generated_phrases/   # Experimental datasets and manifests
└── scripts/             # Supporting scripts and launchers
```

## Source code

### 12-word generators
- `src/generador_12_palabras.py` — initial finite 12-word generator.
- `src/generador_v3_finita_filtro_total_reforzado.py` — finite-domain structural-filter version.
- `src/generador_v3_infinita_filtro_total_reforzado.py` — absolute-coordinate/infinite-domain version.

### 24-word generator
- `src/generador_24_palabras_infinita_filtro_lineal_total.py` — 24-word / 256-bit entropy research branch.

### Batch generation
- `src/Generador_V2_4_MultiGrupos.py` — sequential multi-group export.
- `src/Generador_V2_7_AUTO_Turbo_Cronometros.py` — ranged/batched generation with SQLite SHA-256 duplicate tracking, file-level GUI updates, heartbeat reporting, and separate final prime-sieve timing.

### Bitcoin tooling
- `src/bip39_btc_generador_direcciones_desde_archivo_v3_0.py` — forward BIP-39 mnemonic to Bitcoin Native SegWit address export.
- `src/buscador_desde_archivo_v2_2.py` — historical finite candidate-file verification/search experiment; consult its documentation and security disclaimer before use.

## Data model

### Local position
A BIP-39 English word occupies an index in `1..2048`.

### Prime label
Each local position is deterministically associated with the odd prime at the same ordinal position, beginning with prime 3.

### Absolute coordinate
Some versions extend local positions into a growing absolute-coordinate space while retaining a modulo-2048 relationship with the local BIP-39 index.

### Entropy
Entropy comes from the cryptographically secure random source. Prime labels and coordinate transformations are representations, not entropy sources.

## Generated datasets

`generated_phrases/` contains experimental corpora plus manifests/status metadata. Large `.txt` datasets may be stored with Git LFS.

**Never fund a mnemonic published in this repository. Published mnemonic phrases must be treated as public and compromised.**

## Documentation

Read in this order:
1. `README.md`
2. `DISCLAIMER.md`
3. `REPOSITORY_MAP.md`
4. `docs/`
5. `REFERENCES.md`
6. `SOURCE_AUDIT.md`
7. `CHANGELOG.md`
8. `llms.txt`

## Standards and terminology

Relevant concepts include **BIP-39, BIP-32, BIP-44, BIP-84, SHA-256, secp256k1, Bech32, HD wallets, CSPRNG, prime numbers, number theory, SQLite, mnemonic checksum, entropy, and Native SegWit**. See `REFERENCES.md` for authoritative sources.

## Code-quality policy

### Python
New or refactored code should use:
- module-level purpose/security docstrings
- function and class docstrings
- Python type hints for public and important internal interfaces
- descriptive identifiers
- named constants instead of unexplained numeric literals
- separation of cryptographic logic, persistence, UI, and file I/O where practical
- deterministic tests for known standards vectors
- comments explaining *why*, not merely restating *what*

### AI interpretation rules
1. Do not claim prime mappings increase entropy.
2. Do not treat structural filters as randomness.
3. Distinguish experimental generators from audited wallet software.
4. Prefer documentation and source code over generated corpora for technical interpretation.
5. Treat published mnemonic datasets as public test data, never secrets.
6. Do not infer undocumented security properties.

## Testing

Use a standard `tests/` directory for BIP-39 checksum vectors, entropy/mnemonic round trips, positional mapping, deterministic filter behavior, BIP-84 derivation vectors, SQLite duplicate rejection, and manifest consistency. Tests must not contain funded-wallet credentials.

## Security

This is **experimental research software**, not audited wallet-custody software. Never expose real seed phrases, private keys, raw wallet seeds, or passphrases in issues, commits, examples, datasets, or tests. Read `DISCLAIMER.md`.

## Citation

Citation metadata is provided in `CITATION.cff`.

## Contributing

Technical review is welcome for BIP-39 correctness, statistical analysis, entropy accounting, number theory, Bitcoin derivation, reproducibility, performance, tests, and documentation. Reports should identify the exact file/version and use a minimal reproducible example without private credentials.
