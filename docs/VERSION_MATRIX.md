# Version Matrix

## Purpose

This document summarizes the evolution of the experimental generator family and related tooling.

The matrix is a navigation aid, not a substitute for the exact source files and implementation notes.

## Version evolution

| Version / branch | Main purpose | Key characteristics | Important interpretation |
|---|---|---|---|
| Early finite generator | Initial BIP-39 / prime-position experiment | Finite `1..2048` positional model | Prime mapping is deterministic |
| V3 finite reinforced filter | Finite-domain filtering experiment | Strengthened deterministic structural filters | Filters do not add entropy |
| V3 infinite reinforced filter | Absolute-coordinate experiment | Extends local position into growing coordinate space | Absolute coordinates do not add entropy |
| 24-word infinite branch | 24-word research branch | 256-bit BIP-39 entropy branch | Prime mapping remains deterministic |
| V2.4 MultiGrupos | Multi-group generation | Sequential multi-group export, SQLite duplicate history | Local duplicate control only |
| V2.5 Turbo | Performance-oriented generation | Higher-throughput generation and shared historical DB family | Performance change, not entropy change |
| V2.6 AUTO Turbo | Automated ranges | Start/end range, groups per value/file, automated output | Batch orchestration |
| V2.7 AUTO Turbo | Timing and observability | GUI file/value events, heartbeat, separate timers, parallel prime processing | Adds observability and batch control |
| V2.7 large-DB fix | Historical DB compatibility | Avoids expensive startup `COUNT(*)` behavior while preserving historical DB | Performance/operability fix |
| Address exporter V3.0 | Forward wallet derivation | Known BIP-39 mnemonic -> Native SegWit address | Deterministic public derivation |
| File verifier/search V2.2 | Finite file-based verification | Operates only on user-supplied candidate files | Not an unrestricted cryptographic inversion method |

## Detailed notes

### Early finite generator

The first research stage operates inside the finite 2,048-word BIP-39 index space.

Core representation:

`local position <-> odd-prime ordinal label <-> BIP-39 word`

### Reinforced finite filters

Later finite versions introduce stronger deterministic structural rejection rules.

The filters change which CSPRNG-generated candidates are accepted.

They do not create entropy.

### Infinite / absolute-coordinate versions

These versions extend the finite local coordinate into a growing absolute-position model.

The relationship back to the local BIP-39 position remains deterministic.

### 24-word branch

The 24-word branch explores the same positional ideas with the BIP-39 24-word structure.

For standard BIP-39, 24 words encode 256 entropy bits plus checksum bits.

### V2.4 MultiGrupos

Important characteristics include:

- multiple groups per run
- SQLite phrase-hash tracking
- local duplicate rejection
- output metadata

Historical V2.4 performs more frequent database operations than later optimized versions.

### V2.5 Turbo

Performance-oriented changes reduce overhead in high-volume generation.

The V2.5/V2.6/V2.7 family historically shares the same application data identity for the SQLite history, which is relevant when interpreting performance and database state.

### V2.6 AUTO Turbo

Adds automated range execution and output partitioning.

Typical controls include:

- initial value
- final value
- groups per value
- groups per file
- output prefix/destination

### V2.7 AUTO Turbo

Adds improved observability and execution reporting:

- separate generation timing
- prime-processing timing
- engine heartbeat
- file-level progress
- value-level progress
- multi-worker prime processing

### V2.7 large-database fix

A large historical SQLite database exposed a startup performance issue associated with counting the full `generated` table.

The compatibility fix preserves the historical database while replacing the expensive startup counting strategy with a faster approach appropriate to the application's append-only behavior.

This is a performance fix.

It does not change BIP-39 entropy construction.

### Forward address exporter

The address exporter performs deterministic forward derivation from known mnemonics to public Bitcoin addresses.

This is suitable for validation and reproducibility using public test vectors.

### Finite file verifier

The file-based verifier checks candidates explicitly supplied by the user.

Its scope is finite and input-defined.

## Version interpretation rules

When comparing versions:

1. identify the exact filename
2. distinguish algorithm changes from GUI/performance changes
3. record database state
4. record filter version
5. do not infer entropy increases from prime-coordinate changes
6. do not assume identical performance across storage/database environments

## Historical preservation

Older source files should remain available where practical.

Research history is valuable because it allows reviewers to see:

- what changed
- why it changed
- whether behavior changed
- whether only performance/observability changed

## Future versioning

Future refactoring should preferably separate:

```text
src/core/
src/generators/
src/bitcoin/
src/gui/
```

while keeping historical implementations available for traceability.

## Verification status

The repository currently includes automated tests for selected V2.7 deterministic core behavior and GitHub Actions across multiple Python versions.

Additional version-specific tests should be added progressively.
