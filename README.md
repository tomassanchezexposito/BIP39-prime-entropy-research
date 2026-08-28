# Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research

![Python](https://img.shields.io/badge/Python-3.x-blue)
![BIP39](https://img.shields.io/badge/BIP--39-Research-orange)
![Bitcoin](https://img.shields.io/badge/Bitcoin-Native%20SegWit-yellow)
![Status](https://img.shields.io/badge/status-experimental-red)

> **Experimental research repository. Do not use the included generators as audited wallet-custody software. Never fund a mnemonic that has been published in this repository. Read [`DISCLAIMER.md`](DISCLAIMER.md) before running any generator.**

**Experimental research on prime-number positional mappings, BIP-39 entropy construction, mnemonic generation, Bitcoin wallet security, and Native SegWit derivation.**

This repository documents an experimental line of work connecting two representations built on the same 2,048-element index space:

1. an arithmetic coordinate for odd integers and odd-prime positions, beginning with `C_n = 3 + 2n`; and
2. the 2,048-word BIP-39 English index space, where each word index represents 11 bits.

The project maps each local position `1..2048` to the odd prime at the same ordinal position and to the BIP-39 English word at that index. This creates an auditable representation:

`local position ↔ odd-prime label ↔ BIP-39 word`

**The prime mapping does not create cryptographic entropy.** It is deterministic labeling. In the 12-word generators, the entropy model is 128 bits plus a 4-bit SHA-256 checksum, following the BIP-39 bit structure. When the initial position is fixed by the user, its 11-bit index is fixed and the implementation obtains the remaining 117 bits from Python's `secrets` module. Therefore, if that initial position is known, the CSPRNG contribution of that run is 117 bits. The infinite absolute-prime coordinate and the structural rejection filters likewise do not add entropy.

## Repository contents

- `src/generador_12_palabras.py` — first finite 12-word generator.
- `src/generador_v3_finita_filtro_total_reforzado.py` — strengthened finite-domain structural filter.
- `src/generador_v3_infinita_filtro_total_reforzado.py` — strengthened infinite absolute-coordinate generator.
- `src/generador_24_palabras_infinita_filtro_lineal_total.py` — 24-word / 256-bit-entropy branch.
- `src/Generador_V2_4_MultiGrupos.py` — sequential multi-group export.
- `src/buscador_desde_archivo_v2_2.py` — finite, user-supplied candidate-file Bitcoin verifier/search tool.
- `src/bip39_btc_generador_direcciones_desde_archivo_v3_0.py` — forward BIP-39 mnemonic → Native SegWit address exporter.
- `src/Generador_V2_7_AUTO_Turbo_Cronometros.py` — automatic ranged/batched generation with SQLite duplicate hashes, file-level GUI updates, heartbeat, and separate prime-sieve timing.
- `docs/` — English technical manuscript, version history, and per-program implementation notes.
- `generated_phrases/` — intentionally empty public-data staging area with a manifest/status updater. Only never-funded public test vectors belong there.

## Standards and implementation context

BIP-39 defines mnemonic generation by appending `ENT/32` checksum bits to entropy and splitting the result into 11-bit word indices; 128-bit entropy produces 12 words and 256-bit entropy produces 24 words. BIP-39 also defines an optional passphrase used in PBKDF2-HMAC-SHA512 when deriving the 512-bit seed. Native SegWit account derivation in the Bitcoin utilities follows BIP-84, with the default first receiving path `m/84'/0'/0'/0/0`.

See [`REFERENCES.md`](REFERENCES.md) for authoritative sources.

## Reproducibility note

The Python source snapshots in `src/` are preserved as supplied rather than mechanically translating code strings/comments, because changing executable source solely for language consistency could introduce defects. All repository documentation and the English technical manuscript are in English. Source-file SHA-256 fingerprints are recorded in [`SOURCE_AUDIT.md`](SOURCE_AUDIT.md).

## Generated-data publishing

Large phrase corpora can exceed ordinary GitHub file limits. The repository includes Git LFS rules for generated `.txt` corpora and a script that rebuilds dataset status/manifest files. More importantly, **do not publish any mnemonic that has ever controlled real funds or may be intended to do so**.
