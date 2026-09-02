# Technical Community Post

## Suggested title

Reproducible Python research on BIP-39 entropy and deterministic prime-coordinate mappings

## Post

I have published an independent experimental Python research repository studying BIP-39 mnemonic construction, entropy accounting, deterministic prime-number positional mappings, absolute-coordinate models, structural filters, and Bitcoin wallet derivation tooling.

The project deliberately separates cryptographic randomness from deterministic representation:

- prime mappings do not add entropy
- absolute-coordinate transforms do not add entropy
- structural filters are deterministic
- SQLite duplicate tracking is local history only

The repository now includes automated tests, technical architecture, reproducibility documentation, machine-readable dataset metadata, public experimental datasets, and a Zenodo DOI.

GitHub:
https://github.com/tomassanchezexposito/BIP39-prime-entropy-research

Zenodo:
https://doi.org/10.5281/zenodo.22257814

I would welcome technical review, reproducibility attempts, and criticism of the entropy accounting, coordinate model, test design, or documentation.
