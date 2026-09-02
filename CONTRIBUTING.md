# Contributing

## Purpose

Contributions are welcome when they improve correctness, reproducibility, documentation, testing, statistical interpretation, number-theory analysis, Bitcoin standards compliance, or code quality.

This repository is experimental research software. Contributions must preserve the distinction between cryptographic entropy and deterministic transformations.

## Before contributing

Please read:

1. `README.md`
2. `ARCHITECTURE.md`
3. `DISCLAIMER.md`
4. `docs/SECURITY_MODEL.md`
5. `docs/CODE_QUALITY.md`
6. `docs/GLOSSARY.md`

## Contribution principles

### Preserve research history

Historical generator versions are part of the research record.

Do not silently rewrite historical files merely to modernize style. If a historical implementation must be corrected, document the reason, preserve traceability, and prefer a new version or an explicitly documented patch.

### Do not overstate security

Contributions must not claim that:

- prime-number mappings add cryptographic entropy
- structural rejection filters create randomness
- SQLite duplicate tracking proves global uniqueness
- experimental generators are audited wallet-custody software

### Never submit secrets

Do not include:

- real or funded BIP-39 mnemonics
- private keys
- xprv values
- raw wallet seeds
- passphrases protecting real assets
- exchange/API credentials
- authentication tokens

Published test vectors must be public, never-funded, and clearly identified as test data.

## Code contributions

### Python

New or refactored Python should follow `docs/CODE_QUALITY.md`.

Use:

- type hints for public and important internal interfaces
- meaningful docstrings
- semantic comments explaining assumptions and security boundaries
- descriptive names
- named constants
- clear separation of concerns where practical

### Tests

Add deterministic tests for new pure behavior.

Run locally from the repository root:

```bash
python -m pytest
```

All tests should pass before opening a pull request.

### Test vectors

Prefer:

- official standards vectors
- deterministic synthetic inputs
- public never-funded examples

Do not introduce real wallet secrets.

## Documentation contributions

Documentation should clearly separate:

- source randomness
- checksum bits
- deterministic coordinate mappings
- deterministic filters
- duplicate persistence
- output metadata

When describing an implementation, identify the exact filename/version whenever possible.

## Dataset contributions

Public datasets should progressively include:

```text
DATASET_CARD.md
metadata.json
MANIFIESTO.tsv
SHA256SUMS.txt
```

Use `docs/DATASET_CARD_TEMPLATE.md` and `docs/metadata.schema.json` where applicable.

Generate integrity hashes with:

```bash
python scripts/generate_sha256s.py generated_phrases/<dataset-directory>
```

## Bug reports

Use the GitHub bug-report form.

A useful report includes:

- exact source filename/version
- operating system
- Python version
- minimal reproduction steps
- expected behavior
- actual behavior
- error output

Remove all private credentials before posting logs.

## Research questions

Use the research-question issue form for theoretical, statistical, number-theory, entropy, or standards questions.

Clearly distinguish:

- observation
- hypothesis
- measured result
- inference

## Reproducibility reports

Use the reproducibility-report form when independently testing a documented result.

Include:

- exact commit/release
- source filename/version
- environment
- parameters
- observed result
- whether the result matched

## Pull requests

A pull request should:

1. explain the problem or research improvement
2. identify affected files
3. describe behavioral changes
4. include or update tests where practical
5. update documentation if interpretation changes
6. avoid unrelated refactoring

Keep pull requests focused and reviewable.

## Commit messages

Prefer concise, descriptive messages such as:

```text
Add manifest consistency tests
Document V2.7 entropy boundary
Fix dataset metadata validation
Refactor BIP-39 checksum helper
```

## Review criteria

Contributions may be rejected if they:

- introduce unsupported cryptographic claims
- reduce reproducibility
- hide behavioral changes
- include credential material
- add generated noise or dead code
- duplicate existing implementations without a documented reason
- make the repository harder to interpret

## Citation

If your contribution materially extends the research, identify your contribution clearly in the pull request so authorship and attribution can be discussed transparently.
