# `bip39_btc_generador_direcciones_desde_archivo_v3_0.py` — ordered forward address export

## Motivation
This version reuses the verified BIP-39/BIP-32/BIP-84 address-derivation engine but changes the workflow to a purely forward batch operation: load phrases and export their Bitcoin addresses.

## Core operation
For each detected mnemonic in the input sequence:

`mnemonic → BIP-39 seed → BIP-32/BIP-84 child key → compressed public key → P2WPKH Native SegWit address`

Default derivation path: `m/84'/0'/0'/0/0`.

## Order-preserving file processing
The added ordered iterators support TXT, CSV/TSV, and XLSX. They intentionally do **not** remove repeated phrases because doing so would break line/record correspondence.

The exporter writes one output line per detected candidate in the same order. A valid phrase produces its `bc1q...` address. If validation or derivation fails after a candidate is detected, the corresponding output position is retained with an `ERROR_BIP39:<reason>` marker.

## Why this version is useful
It allows a separately generated mnemonic corpus to be converted into a line-aligned public-address corpus without performing an address-to-mnemonic search.

## Security
Input mnemonics are wallet credentials. Use only test vectors or private data under your control. Do not commit real recovery phrases to a public repository.
