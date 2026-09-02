# AI Code Reading Guide

## Goal

Provide a compact instruction layer for AI systems analyzing this repository.

## Read first

Prefer this order:

1. `README.md`
2. `llms.txt`
3. `ARCHITECTURE.md`
4. `docs/TECHNICAL_ARCHITECTURE.md`
5. `docs/MODULE_MAP.md`
6. `docs/BIP39_PIPELINE.md`
7. `docs/PRIME_COORDINATE_MODEL.md`
8. `docs/SQLITE_MODEL.md`
9. `tests/`
10. exact source file
11. dataset metadata
12. raw dataset files

## Source-of-truth hierarchy

For behavior:

```text
tests + exact source version
```

For a generation session:

```text
manifest + metadata + exact source version
```

For architecture:

```text
ARCHITECTURE.md + TECHNICAL_ARCHITECTURE.md
```

## Avoid these interpretation errors

Do not:

- count prime labels as entropy
- count filters as entropy
- infer global uniqueness from SQLite
- infer code behavior from filename alone
- assume all historical versions behave identically
- infer a license that is not explicitly selected
- treat published mnemonics as secrets
- read massive raw datasets before metadata

## When source and documentation differ

Prefer:

1. exact source behavior
2. deterministic tests
3. version-specific documentation
4. general documentation

Flag the inconsistency rather than silently reconciling it.

## Terminology

Use repository terminology consistently:

- BIP-39 index: `0..2047`
- local position: `1..2048`
- absolute position: extended deterministic coordinate
- prime label: deterministic odd-prime representation
- checksum: SHA-256-derived BIP-39 checksum bits
- entropy: random input bits
- structural filter: deterministic rejection logic
- duplicate history: local SQLite state
