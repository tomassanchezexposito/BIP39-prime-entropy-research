# `generador_v3_infinita_filtro_total_reforzado.py` — strengthened infinite-coordinate generator

## Purpose
This version combines the BIP-39-compatible 12-word entropy/checksum structure with the project's infinite absolute-coordinate representation and a strengthened structural filter.

## Local versus absolute positions
A word is selected by a local position:

`local(g) = ((g - 1) mod 2048) + 1`

After the first absolute position, each new generated local index is lifted to the *first strictly later* absolute position with that local residue. Therefore, the absolute sequence always increases even if the local symbol decreases numerically.

This coordinate system is an ordering/representation layer; it does not add entropy to the mnemonic.

## Structural rejection
The implementation rejects:

- fixed-step modular progressions;
- strict ascending/descending local order with arbitrary gaps under the implemented one-cycle criterion;
- twelve-position consecutive local ranges, including wrap-around at `2048 ↔ 1`.

## Absolute-prime calculation
After a candidate is accepted, the implementation can calculate the odd prime at each requested absolute ordinal using a segmented sieve. It estimates an upper bound, generates base primes up to the square root of the working range, and sieves odd numbers in bounded segments.

## Duplicate control
A SHA-256 hash of each phrase is stored in local SQLite history. Duplicate hashes are rejected and regenerated.

## Performance boundary
The manuscript explicitly notes that very large absolute positions make pure-Python prime lookup increasingly expensive. The infinite coordinate does not imply constant-time access to arbitrarily distant primes.
