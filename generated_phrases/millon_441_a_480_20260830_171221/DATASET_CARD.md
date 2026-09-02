# Dataset Card: millon_441_a_480_20260830_171221

## Summary

**Dataset ID:** `millon_441_a_480_20260830_171221`

**Purpose:** Public experimental BIP-39 mnemonic dataset produced for reproducibility, statistical inspection, and implementation research.

**Security classification:** Public test data. **Never use any mnemonic in this dataset to secure real funds.**

## Provenance

### Generator

- Generator file: `Generador_V2_7_AUTO_Turbo_Cronometros.py`
- Generator version: `2.7`
- Repository: `https://github.com/tomassanchezexposito/BIP39-prime-entropy-research`
- Git commit/revision: `unknown for this historical generation session`
- Python version: `unknown for this historical generation session`

### Generation session

- Dataset directory: `millon_441_a_480_20260830_171221`
- Directory timestamp encoded in name: `2026-08-30 17:12:21`
- Start value: `441`
- End value: `480`
- Values processed: `40`
- Groups per value: `1,000,000`
- Groups per file: `1,000,000`
- Total generated groups: `40,000,000`
- Output mnemonic files: `40`
- Manifest rows: `40`
- Completion state: all manifest rows report `COMPLETO`

## BIP-39 model

### Mnemonic length

`12` words

### Entropy construction

This dataset is associated with the documented V2.7 12-word generation design:

- BIP-39 entropy payload: `128 bits`
- first BIP-39 position: fixed by the session value
- known fixed first index contribution: `11 bits`
- CSPRNG-generated remainder: `117 bits`
- checksum: `4 SHA-256-derived bits`
- random source: Python `secrets` / operating-system CSPRNG

The checksum is deterministic and is not additional entropy.

## Prime-coordinate interpretation

The prime-number positional mapping is deterministic metadata.

**It does not add cryptographic entropy.**

For this dataset:

- local-position model: `1..2048`
- prime-label convention: ordinal odd primes beginning with `3`
- first absolute position for each value equals the manifest `valor`
- the manifest records the next absolute position after each value's one-million-group run

The `siguiente_posicion_absoluta` values in the manifest range from approximately 11.266 billion to 11.274 billion.

## Structural filters

The V2.7 generator applies its documented deterministic structural rejection filter before accepting a candidate.

Structural filters may alter the accepted-output distribution, but they do not generate randomness and must not be counted as entropy.

## Duplicate policy

The V2.7 generator uses SQLite with SHA-256 hashes of emitted phrases to reduce local re-emission relative to the database history available to that installation.

Important limitations:

- this is local duplicate tracking
- it does not prove global uniqueness
- resetting or replacing the database changes the duplicate history
- duplicate tracking does not add entropy

## Files

### Manifest

`MANIFIESTO.tsv`

The manifest records one row for each value from `441` through `480`.

### Mnemonic files

Pattern:

`millon_valor_XXXXXX_parte_0001.txt`

Examples:

- `millon_valor_000441_parte_0001.txt`
- `millon_valor_000480_parte_0001.txt`

Each manifest row reports `1,000,000` generated groups.

### Integrity hashes

`SHA256SUMS.txt`

This file should be regenerated after adding or changing `DATASET_CARD.md` or `metadata.json`.

## Manifest-derived consistency checks

The manifest reports:

- first global group: `1`
- last global group: `40,000,000`
- continuous one-million-group blocks
- start value: `441`
- end value: `480`
- 40 output files
- every row marked `COMPLETO`

These values are internally consistent with a 40-value × 1,000,000-groups-per-value generation plan.

## Verification

Recommended procedure:

1. verify file hashes using `SHA256SUMS.txt`
2. compare file/group counts against `MANIFIESTO.tsv`
3. identify the exact V2.7 source revision used for the historical run if later recovered
4. reproduce a small controlled sample with the documented generator
5. independently validate BIP-39 checksum behavior where relevant

## Known limitations

- Experimental research software, not audited custody software.
- Published mnemonics are public and compromised.
- Prime labels do not add entropy.
- Structural filters do not add entropy.
- SQLite duplicate tracking is local, not global.
- Exact Git commit and Python runtime for this historical generation session are not recorded in the manifest.
- The directory timestamp is inferred from the dataset directory name, not from a dedicated manifest timestamp field.

## Citation

Use the repository `CITATION.cff` metadata when citing the software.

For this dataset, identify at minimum:

- dataset ID: `millon_441_a_480_20260830_171221`
- generator: `Generador_V2_7_AUTO_Turbo_Cronometros.py`
- version: `2.7`
- range: `441..480`
- total generated groups: `40,000,000`
- repository revision/release if known at citation time
