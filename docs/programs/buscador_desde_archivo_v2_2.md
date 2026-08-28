# `buscador_desde_archivo_v2_2.py` — finite candidate-file Bitcoin verifier

## Scope
This utility adds Bitcoin Native SegWit derivation to BIP-39 phrase processing. Its source header defines two principal operations:

1. a known 12-word BIP-39 mnemonic → Native SegWit address; and
2. a Bitcoin address → search **only within the finite phrases loaded from a user-selected TXT/CSV/XLSX file**.

It does not mathematically invert a Bitcoin address.

## Bitcoin derivation path
Default path: `m/84'/0'/0'/0/0`.

The implementation contains pure-Python routines for:

- BIP-39 NFKD normalization and checksum validation;
- PBKDF2-HMAC-SHA512 mnemonic-to-seed conversion;
- BIP-32 private child derivation;
- secp256k1 scalar multiplication and compressed public keys;
- HASH160 and Bech32 P2WPKH address encoding.

## Candidate-file loading
TXT, CSV/TSV, and XLSX readers extract 12-word candidate phrases and validate the BIP-39 checksum before they are available to the search function.

## Search behavior
The address-search loop derives the configured address for each *already supplied* valid candidate and compares it with the target. Consequently, runtime is proportional to the finite candidate set and the cost of key derivation.

## Responsible-use boundary
This snapshot is included for reproducibility and authorized finite-candidate verification. It should not be modified or deployed to search third-party seed material, leaked recovery lists, or wallets the operator is not authorized to analyze.
