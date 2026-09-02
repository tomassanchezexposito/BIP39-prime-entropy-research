# BIP-39 Pipeline

## Scope

This document describes the BIP-39 construction logic used by the documented 12-word generator path.

## BIP-39 word space

The English BIP-39 wordlist contains:

```text
2048 words
```

Therefore each word index requires:

```text
11 bits
```

because:

```text
2^11 = 2048
```

## 12-word structure

For a standard 12-word mnemonic:

```text
entropy:   128 bits
checksum:    4 bits
-------------------
total:      132 bits
```

The 132 bits are split into:

```text
12 × 11-bit indexes
```

## V2.7 fixed-first-position model

When the first BIP-39 position is fixed and known:

```text
first index: 11 fixed bits
random tail: 117 CSPRNG bits
----------------------------
entropy:     128 bits
```

The implementation uses the first index as the high 11 bits and fills the remaining 117 bits using Python `secrets`.

## Checksum

The 128-bit entropy is serialized to 16 bytes.

SHA-256 is calculated.

For the 12-word path, the first four hash bits become the checksum.

```text
checksum = first 4 bits of SHA256(entropy)
```

The checksum is deterministic.

It is not entropy.

## Index extraction

The entropy and checksum are concatenated into a 132-bit value.

That value is split into twelve 11-bit indexes.

```text
index[0]
index[1]
...
index[11]
```

Each index must be in:

```text
0..2047
```

## Word lookup

Each index selects the word at that index in the BIP-39 English wordlist.

## Local position convention

The repository frequently exposes a 1-based positional representation:

```text
local_position = bip39_index + 1
```

Therefore:

```text
BIP-39 index: 0..2047
local position: 1..2048
```

## Important distinction

Do not confuse:

- entropy bits
- checksum bits
- word indexes
- local positions
- prime labels
- absolute coordinates

Only the documented CSPRNG contribution is random input.

## 24-word branch

The repository also contains a 24-word research branch.

Standard BIP-39 24-word construction uses:

```text
256 entropy bits
8 checksum bits
264 total bits
24 × 11-bit indexes
```

Exact behavior should always be confirmed against the specific source version.
