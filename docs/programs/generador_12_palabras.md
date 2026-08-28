# `generador_12_palabras.py` — finite 12-word generator

## Purpose and development role
This is the first finite generator in the software lineage. It converts a user-selected initial position in `1..2048` into the first 11 bits of a 128-bit entropy field, generates the remaining 117 bits with `secrets.randbits(117)`, appends the 4-bit SHA-256 checksum, and maps the resulting twelve 11-bit indices to the project data table.

## Data model
`datos_2048.json` must contain exactly 2,048 ordered records. Each record binds a local position to an odd prime and a word. The program validates that positions are exactly `1..2048`, words are unique, and primes form a strictly increasing set of odd primes.

The prime is not used to create entropy. It is a deterministic label for the same index represented by the word.

## Generation algorithm
1. Validate `first_position ∈ [1,2048]`.
2. Convert to zero-based `first_index = first_position - 1`.
3. Draw `random_tail = secrets.randbits(117)`.
4. Form `entropy_int = (first_index << 117) | random_tail`.
5. Compute the first four bits of `SHA256(entropy_bytes)`.
6. Append those checksum bits and split the 132-bit result into twelve 11-bit indices.
7. Map indices to positions, odd-prime labels, and words.
8. Hash the complete phrase with SHA-256 and insert only that hash in local SQLite history.
9. If the hash already exists locally, discard the duplicate and retry.
10. Display the result in Tkinter.

## Security interpretation
For a *known fixed* initial position, only 117 entropy-field bits are chosen by the CSPRNG. `2^128` describes the total valid 12-word encoding space across all 2,048 possible initial indices, not the unpredictable continuation space of one known fixed-index run.

The local SQLite database is not a global uniqueness service. Two independent installations have no shared registry.

## Dependencies and runtime
The implementation uses only the Python standard library, including `secrets`, `hashlib`, `sqlite3`, `json`, and `tkinter`. Python 3.10+ is the safest baseline for the syntax used by the project snapshots.

## Source fingerprint
See `SOURCE_AUDIT.md` for the exact SHA-256 hash of the supplied source snapshot.
