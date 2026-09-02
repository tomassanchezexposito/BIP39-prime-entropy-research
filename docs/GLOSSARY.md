# Glossary

## Absolute position

A 1-based coordinate used by some generator versions to extend the finite local BIP-39 positional model. It is a deterministic coordinate, not an entropy source.

## BIP-32

Bitcoin Improvement Proposal defining hierarchical deterministic (HD) wallets.

## BIP-39

Bitcoin Improvement Proposal defining mnemonic codes for representing entropy. The English wordlist contains 2,048 words, so each word index represents 11 bits.

## BIP-44

A convention for hierarchical deterministic wallet derivation paths.

## BIP-84

A derivation convention for Native SegWit (P2WPKH) accounts.

## Block

In this repository's positional model, a group associated with the repeated 2,048-position local coordinate space. This project-specific term must not be confused with a Bitcoin blockchain block.

## Checksum

Bits derived from SHA-256 and appended to BIP-39 entropy before splitting the resulting bit string into 11-bit word indices. Checksum bits are not additional entropy.

## CSPRNG

Cryptographically Secure Pseudorandom Number Generator. Where documented, Python's `secrets` module is the project's source of cryptographically relevant randomness.

## Entropy

Random information used to construct a BIP-39 mnemonic. Deterministic prime labels, coordinate mappings, and filters are not entropy sources.

## Generated group

A generated mnemonic record or unit in the batch-generation workflow, depending on the generator version and manifest terminology.

## HD wallet

Hierarchical deterministic wallet. A wallet structure in which keys and addresses can be derived from a root seed according to defined paths.

## Local position

A 1-based position in the range `1..2048`, corresponding to a BIP-39 English word index plus one.

## MANIFEST

A tabular metadata file describing generated output files, ranges, group numbers, positional metadata, and completion state.

## Mnemonic

A BIP-39 word sequence representing entropy plus checksum. Any mnemonic published in this repository is public test data and must not secure real assets.

## Native SegWit

Bitcoin Segregated Witness output format commonly associated with Bech32 addresses and BIP-84 derivation for P2WPKH.

## Odd-prime label

The odd prime associated deterministically with a local ordinal position. It is metadata/representation and does not add cryptographic entropy.

## Prime mapping

The deterministic relation between local BIP-39 position and ordinal odd-prime label studied by this repository.

## Structural filter

A deterministic rule that accepts or rejects candidate position sequences. It changes the accepted distribution but does not generate randomness.

## SQLite duplicate tracking

Local persistence of SHA-256 phrase hashes used by later generators to reduce re-emission of phrases already recorded in that database. It does not establish global uniqueness.

## Word index

The 0-based BIP-39 wordlist index `0..2047`. Repository user interfaces may also expose the corresponding 1-based local position `1..2048`.
