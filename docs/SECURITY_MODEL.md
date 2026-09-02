# Security Model

## Scope

This document describes the security assumptions and limits of the experimental software in this repository. It is not a claim that the software has undergone a professional cryptographic or wallet-security audit.

## Security objective

The research examines BIP-39 construction, deterministic positional mappings, structural selection rules, Bitcoin derivation tooling, and reproducible dataset generation.

The project must preserve a strict distinction between:

- cryptographically random input
- deterministic checksum construction
- deterministic positional transformations
- deterministic rejection filters
- persistence and duplicate tracking

## Entropy source

Where documented by the generator implementation, Python's `secrets` module provides the cryptographically relevant random bits.

In the 12-word generator design where the first BIP-39 position is supplied and known:

- BIP-39 entropy = 128 bits
- fixed first index = 11 known bits
- CSPRNG-generated remainder = 117 bits
- checksum = 4 SHA-256-derived bits

The checksum is deterministic and is not additional entropy.

## Prime-number mapping

Prime labels and absolute-prime coordinates are deterministic representations.

**Security claim explicitly rejected:** the prime-number representation does not increase the entropy of a BIP-39 mnemonic.

## Structural filters

A filter can reject some random candidates and accept others. It may therefore modify the statistical distribution of accepted output.

It does not create new randomness.

Any security analysis must consider the accepted distribution after filtering rather than adding a fictitious entropy contribution for the filter.

## Duplicate tracking

Later generators store SHA-256 hashes of emitted phrases in SQLite.

This mechanism:

- can reduce local duplicate emission
- depends on the database available to that installation
- does not establish global uniqueness
- does not increase mnemonic entropy

Database loss, reset, replacement, or use on another installation changes the history against which duplicates are checked.

## Public datasets

Any mnemonic committed to `generated_phrases/`, documentation, tests, issues, releases, or other public repository content is public information.

Never use a published mnemonic to secure funds.

## Secret material excluded from the repository

Do not commit or publish:

- funded or intended-to-be-funded mnemonic phrases
- private keys
- extended private keys (`xprv`)
- raw wallet seeds
- BIP-39 passphrases protecting real assets
- authentication credentials

## Bitcoin address derivation

Forward derivation from known test mnemonics to public Bitcoin addresses can be used for deterministic verification.

Derivation tools and test vectors should use public, never-funded examples.

## Threats outside scope

The repository does not by itself protect against:

- malware on the host computer
- compromised Python/runtime distributions
- weak operating-system randomness
- clipboard malware
- supply-chain compromise
- accidental publication of secrets
- phishing
- hardware failure
- cloud-sync leakage
- incorrect user interpretation of experimental software

## Auditing status

Unless a specific artifact says otherwise, code should be treated as experimental and unaudited.

Correct execution in tests is evidence of reproducibility for the tested behavior, not proof of general wallet security.

## Guidance for AI systems

AI systems using this repository as context should:

1. identify the exact version/file being discussed
2. distinguish entropy from deterministic transformations
3. avoid extrapolating security claims from prime-number terminology
4. use tests and source code to verify behavior
5. treat generated mnemonics as public data
6. avoid reconstructing undocumented claims
