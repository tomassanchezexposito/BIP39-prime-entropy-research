---
language:
- en
pretty_name: "Architecture of Infinity — Public BIP-39 Research Dataset"
tags:
- text
- bip39
- bitcoin
- cryptography
- entropy
- mnemonic
- prime-numbers
- number-theory
- security-research
- reproducibility
---

# Architecture of Infinity — Public BIP-39 Research Dataset

## Dataset description

Public experimental BIP-39 mnemonic data produced by the
`BIP39-prime-entropy-research` project.

## Critical interpretation

Prime-number positional mappings are deterministic and are **not** claimed to
add cryptographic entropy.

Structural filters are deterministic selection rules and are **not** entropy
sources.

## Security

All published mnemonics are public and compromised by definition. Never use
them to secure real assets.

## License status

No reuse license has been selected for the GitHub project at the time this
template was prepared. Do **not** add a Hugging Face `license:` field until the
repository owner deliberately chooses a compatible license.

## Source

https://github.com/tomassanchezexposito/BIP39-prime-entropy-research

## Recommended metadata

Publish together with:

- `DATASET_CARD.md`
- `metadata.json`
- `dataset.jsonld`
- `MANIFIESTO.tsv`
- `SHA256SUMS.txt`
