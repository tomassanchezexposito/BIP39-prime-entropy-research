# API Reference

## Scope

This is a semantic reference for important functions already exposed by historical research code.

It is not a promise of a stable public Python package API.

## V2.7 core functions

### `local_position(absolute_position: int) -> int`

Purpose:

Map a positive 1-based absolute position into the local 1-based `1..2048` space.

Conceptual formula:

```text
((absolute_position - 1) mod 2048) + 1
```

Properties:

- deterministic
- periodic every 2048 positions
- rejects non-positive input

### `block_number(absolute_position: int) -> int`

Purpose:

Return the zero-based block associated with a positive absolute position.

Conceptual formula:

```text
(absolute_position - 1) // 2048
```

Properties:

- deterministic
- block 0 corresponds to absolute positions `1..2048`

### `checksum4(entropy_bytes: bytes) -> int`

Purpose:

Return the four BIP-39 checksum bits used by the 12-word / 128-bit entropy path.

Conceptual behavior:

```text
SHA256(entropy_bytes)[first byte] >> 4
```

### `indexes_from_entropy(entropy_int: int) -> tuple[list[int], int]`

Purpose:

Construct twelve BIP-39 word indexes from a 128-bit entropy integer.

Conceptual flow:

```text
entropy integer
    ↓
16 entropy bytes
    ↓
4-bit SHA-256 checksum
    ↓
132-bit combined value
    ↓
12 × 11-bit indexes
```

Returns:

- list of twelve indexes in `0..2047`
- four-bit checksum value

### `build_candidate_fast(first_absolute, items, con)`

Purpose:

Build one accepted candidate using the V2.7 generation flow.

High-level behavior:

1. convert first absolute position to local position
2. derive first BIP-39 index
3. generate 117 random tail bits
4. construct 128-bit entropy
5. build valid BIP-39 indexes/checksum
6. apply deterministic structural filter
7. map indexes to words
8. hash phrase with SHA-256
9. insert into SQLite using duplicate-safe logic
10. lift local positions into absolute positions
11. return structured candidate metadata

Security interpretation:

- randomness comes from the CSPRNG tail
- prime/coordinate mappings do not add entropy
- SQLite does not add entropy

## Dataset tool functions

### `sha256_file(path)`

Purpose:

Compute SHA-256 file integrity digest.

### `read_manifest(path)`

Purpose:

Read a TSV generation manifest into normalized dictionaries.

### `manifest_summary(rows)`

Purpose:

Derive machine-readable session statistics from recognized manifest columns.

### `build_metadata(...)`

Purpose:

Construct project-specific dataset metadata.

### `build_jsonld(metadata)`

Purpose:

Construct schema.org `Dataset` JSON-LD.

### `build_card(metadata)`

Purpose:

Render human/AI-readable dataset documentation.

## API stability

Historical generator functions are research implementation details.

When building new reusable modules, stable public interfaces should be placed in dedicated modules under the future modular architecture rather than relying on historical GUI files.
