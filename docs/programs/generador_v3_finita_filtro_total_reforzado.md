# `generador_v3_finita_filtro_total_reforzado.py` — strengthened finite filter

## Purpose
This branch keeps the finite `1..2048` local domain while adding stronger rejection rules to the 12-word generator.

## Entropy construction
The entropy/checksum mechanism remains 128 + 4 bits. The selected initial position fixes the first 11 bits, while the remaining 117 bits come from `secrets`.

## Structural rejection layer
The program rejects candidates matching any of these implemented conditions:

- a fixed-step progression modulo 2048, including step zero;
- strict ascending or descending local order;
- a set of twelve consecutive local positions regardless of their original order;
- an explicit ordered-consecutive condition.

A candidate that matches a rejected pattern is discarded and a new CSPRNG continuation is generated.

## What the filter means
The filter is a policy on accepted output. A cryptographically random source can naturally produce an ordered-looking result, so rejection must not be described as proving that a candidate lacks entropy. The accepted distribution is the original generation process conditioned on passing the filter.

## Duplicate handling
The emitted phrase is SHA-256 hashed and checked against local SQLite history. Only the hash and metadata are retained by this mechanism.

## Limitations
The finite model does not preserve a globally increasing absolute-prime coordinate; its symbol domain is the local 2,048-element map. It remains experimental and unaudited for custody.
