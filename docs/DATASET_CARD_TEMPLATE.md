# Dataset Card: <DATASET_ID>

## Summary

**Dataset ID:** `<DATASET_ID>`

**Purpose:** Public experimental BIP-39 mnemonic dataset for reproducibility and research.

**Security classification:** Public test data. **Never use any mnemonic in this dataset to secure real funds.**

## Provenance

### Generator

- Generator file: `<GENERATOR_FILENAME>`
- Generator version: `<GENERATOR_VERSION>`
- Repository: `https://github.com/tomassanchezexposito/BIP39-prime-entropy-research`
- Git commit/revision: `<COMMIT_OR_UNKNOWN>`
- Python version: `<PYTHON_VERSION_OR_UNKNOWN>`

### Generation session

- Created: `<ISO_8601_DATE_OR_UNKNOWN>`
- Start value: `<START_VALUE>`
- End value: `<END_VALUE>`
- Values processed: `<VALUE_COUNT>`
- Groups per value: `<GROUPS_PER_VALUE>`
- Groups per file: `<GROUPS_PER_FILE>`
- Total generated groups: `<TOTAL_GROUPS>`
- Output files: `<OUTPUT_FILE_COUNT>`

## BIP-39 model

### Mnemonic length

`<12_OR_24>` words

### Entropy construction

Describe the exact implementation used for this dataset.

For the documented 12-word V2.7 design with a fixed known first position:

- BIP-39 entropy payload: 128 bits
- fixed first word index: 11 bits
- CSPRNG-generated remainder: 117 bits
- checksum: 4 SHA-256-derived bits
- random source: Python `secrets` / operating-system CSPRNG

## Prime-coordinate interpretation

The prime-number positional mapping is deterministic metadata.

**It does not add cryptographic entropy.**

## Structural filters

Filter implementation/version:

`<FILTER_DESCRIPTION>`

Structural filters are deterministic selection rules. They may modify the distribution of accepted outputs but do not create randomness.

## Duplicate policy

`<SQLITE_OR_OTHER_POLICY>`

Local duplicate tracking does not prove global uniqueness.

## Files

- Manifest: `<MANIFEST_FILENAME>`
- Mnemonic file pattern: `<FILE_PATTERN>`
- Integrity hashes: `SHA256SUMS.txt`

## Verification

1. verify file hashes
2. compare file/group counts with the manifest
3. identify the exact generator source/version
4. reproduce a small controlled sample if practical
5. validate BIP-39 checksum behavior independently when relevant

## Known limitations

- Experimental research software, not audited custody software.
- Published mnemonics are public and compromised.
- Prime labels do not add entropy.
- Structural filters do not add entropy.
- SQLite duplicate tracking is local, not global.

## Citation

Use the repository `CITATION.cff`. For independent dataset citation, include dataset ID, repository revision/release, generator version, and creation date where available.
