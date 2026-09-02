# Prime Coordinate Model

## Purpose

This document isolates the project's number-theory representation from the BIP-39 entropy model.

## Local coordinate

The local coordinate is:

```text
1..2048
```

It corresponds to:

```text
BIP-39 index + 1
```

## Odd-prime label

Each local position is associated with the odd prime having the same ordinal position when the sequence begins with prime `3`.

Conceptually:

```text
local position 1 -> 3
local position 2 -> 5
local position 3 -> 7
...
```

The prime is a deterministic label.

## What the mapping means

The mapping allows the project to represent a BIP-39 word position using a number-theory label.

Conceptually:

```text
local position
      ↕
odd-prime ordinal
      ↕
BIP-39 word
```

## What the mapping does not mean

The prime label does not:

- generate new entropy
- hide the original local position
- make a known mnemonic harder to reconstruct
- replace BIP-39 security assumptions

## Absolute position

Some versions define an absolute coordinate extending beyond the first local block.

Local position is recovered deterministically by wrapping through the 2,048-position space.

Conceptually:

```text
absolute position
       ↓
block number + local position
```

## Block number

The zero-based block is:

```text
(absolute_position - 1) // 2048
```

## Local recovery

The local position is:

```text
((absolute_position - 1) mod 2048) + 1
```

## Prime extraction

For large absolute prime coordinates, later versions use segmented prime-processing logic to obtain selected ordinal primes efficiently.

This is a computational technique for obtaining labels.

It does not affect BIP-39 entropy.

## Research use

The coordinate system is useful for:

- traceability
- positional experiments
- number-theory analysis
- deterministic labeling
- studying filter behavior across extended coordinates

## AI interpretation rule

Whenever prime terminology appears, separate:

```text
mathematical representation
```

from:

```text
cryptographic randomness
```

They are not equivalent.
