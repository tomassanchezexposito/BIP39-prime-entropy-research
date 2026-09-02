# Scholarly Discovery Strategy

## Goal

Make the research easy to identify, cite, verify, and connect to related scholarly objects.

## Persistent identity

A DOI provides a persistent identifier independent of the current GitHub URL.

Use version-specific identifiers when exact reproducibility matters.

## Metadata consistency

Keep these fields semantically consistent across GitHub, Zenodo, future dataset repositories, and publications:

```text
title
creator
project description
keywords
version
release date
repository URL
DOI
license status
```

## Recommended keywords

```text
BIP-39
Bitcoin
cryptographic entropy
mnemonic
SHA-256
prime numbers
number theory
HD wallet
BIP-84
Native SegWit
reproducibility
Python
research software
dataset
```

## Research-object separation

Treat these as potentially separate citable objects:

1. research software
2. technical manuscript/report
3. generated dataset collection
4. individual large/versioned datasets
5. future peer-reviewed publication

Connect them through related identifiers rather than forcing all material into one archival object.

## ORCID

If the author has an ORCID, use the real ORCID consistently in scholarly metadata.

If no ORCID exists, do not fabricate one.

## Future publication targets

After the repository and software release have a stable DOI, consider:

- a technical preprint/report describing the methodology
- a dataset deposit for selected reproducible corpora
- a software-oriented scholarly publication if the implementation becomes sufficiently reusable
- relevant cryptography, Bitcoin, reproducible-research, Python, and number-theory communities

## Discovery principle

Good scholarly discovery comes primarily from:

```text
persistent identifiers
+ accurate metadata
+ citations/backlinks
+ reproducible artifacts
+ external discussion
+ clear scope
```

not from keyword repetition.
