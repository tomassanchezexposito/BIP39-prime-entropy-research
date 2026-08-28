# `generador_24_palabras_infinita_filtro_lineal_total.py` — 24-word infinite branch

## Purpose
This branch extends the same local/absolute coordinate idea to the BIP-39 24-word bit structure.

## Entropy and checksum
For 24 words:

- entropy field: 256 bits;
- checksum: 8 bits (`256 / 32`);
- encoded total: 264 bits;
- 24 indices × 11 bits = 264 bits.

The selected initial local position fixes the first 11 bits. The implementation obtains the remaining 245 bits with the operating-system-backed `secrets` CSPRNG.

## Infinite position model
The 2,048 local symbols repeat across an unbounded positive absolute coordinate. Each later local symbol is lifted to its first later absolute occurrence, making absolute positions and corresponding absolute primes strictly increasing.

## Filtering
The program rejects fixed-step modular progressions, strict ascending/descending local traversals under its implemented criterion, and the degenerate repeated-position case covered by step zero.

## Duplicate history
Only a SHA-256 hash of the phrase is placed in the local SQLite duplicate-history table; the duplicate-control mechanism does not establish global uniqueness.

## Security note
The infinite coordinate does not increase the 256-bit entropy field. If the initial 11-bit position is known, this implementation's random tail contains 245 CSPRNG-generated bits.
