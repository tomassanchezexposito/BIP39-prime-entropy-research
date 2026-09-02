# Code Quality Policy

## Purpose

This policy defines how new or refactored code should be written so that the repository remains understandable, reproducible, and easy to inspect by humans, static-analysis tools, and AI systems.

## Historical code

Historical generator versions are part of the research record. Do not rewrite them merely to satisfy style rules. Corrections to historical files should be explicit, documented, and versioned.

## New Python code

### Type hints

Public functions and important internal interfaces should use Python type hints.

```python
def local_position(absolute_position: int) -> int:
    ...
```

### Docstrings

Modules, public classes, and public functions should explain purpose, inputs, outputs, assumptions, and security-relevant behavior.

A useful cryptographic docstring must distinguish random input from deterministic transformation.

### Semantic comments

Comments should explain **why** a rule exists or what assumption it preserves.

Good:

```python
# Prime labels are deterministic metadata and must not be counted as entropy.
```

Avoid:

```python
i += 1  # Increment i by one.
```

### Naming

Use descriptive names. Avoid ambiguous abbreviations unless they are established standards such as BIP, SHA, CSPRNG, or DB.

### Constants

Use named constants for protocol sizes and project invariants rather than unexplained numeric literals.

### Separation of concerns

New architecture should separate, where practical:

- entropy and BIP-39 construction
- prime/coordinate mapping
- structural filters
- Bitcoin derivation
- persistence
- file/manifest output
- GUI
- orchestration

### Error handling

Do not silently ignore cryptographic validation failures. Errors affecting checksum, index bounds, persistence, or derivation should fail explicitly or be recorded clearly.

## Tests

Every new pure transformation should have deterministic tests.

Priority areas:

- BIP-39 checksum construction
- entropy-to-index conversion
- local/absolute position mapping
- prime-label mapping
- deterministic filters
- BIP-84 derivation using public test vectors
- SQLite duplicate handling
- manifest consistency

Never use credentials protecting real funds in tests.

## Security claims

Code comments and documentation must not claim:

- that prime-number mapping adds entropy
- that a rejection filter creates randomness
- that SQLite provides global uniqueness
- that experimental software is audited wallet software

## AI-readability rules

For machine-readable clarity:

1. Keep one concept per function where practical.
2. State units and index bases explicitly (`0-based`, `1-based`, bits, bytes).
3. Prefer structured return types over undocumented positional tuples in new code.
4. Keep protocol names in identifiers/docstrings when relevant (`bip39`, `bip84`, `sha256`).
5. Document deterministic versus random operations.
6. Avoid dead code and unexplained alternate implementations.
7. Preserve version history instead of overwriting behavior without explanation.
