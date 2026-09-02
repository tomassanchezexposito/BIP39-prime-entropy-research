# Tests

## Purpose

This directory contains deterministic verification tests for the research code.

Tests must verify documented behavior without using real wallet credentials or funded mnemonic phrases.

## Initial coverage

The first test module verifies pure functions in `src/Generador_V2_7_AUTO_Turbo_Cronometros.py`:

- 1-based local-position wrapping across the 2,048-position space
- zero-based block numbering
- BIP-39 128-bit zero-entropy checksum/index construction

## Running

From the repository root:

```bash
python -m pytest
```

Install pytest if it is not already available:

```bash
python -m pip install pytest
```

## Expansion priorities

Future tests should cover prime ordinal mapping, structural filters, BIP-84 public vectors, SQLite duplicate behavior, and manifest consistency.

Do not add private keys, real seed phrases, passphrases, or credentials protecting assets.
