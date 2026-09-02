# Zenodo Publication Guide

## Objective

Create a persistent, citable archival record for the software/research repository.

## Recommended publication model

Use the GitHub–Zenodo integration for versioned software releases.

The repository's `CITATION.cff` should remain the primary citation metadata source unless Zenodo-specific metadata is later required.

Do not add `.zenodo.json` merely for duplication: when both `.zenodo.json` and `CITATION.cff` exist, Zenodo prioritizes `.zenodo.json` for GitHub release archiving.

## Before connecting Zenodo

Verify:

- repository is public
- default branch is `main`
- tests pass
- `CITATION.cff` is valid
- author name is correct
- repository title is correct
- no real wallet secrets are present
- release contents are appropriate for permanent archival
- license status is explicitly understood

## First archival release

Recommended first archival tag:

```text
v1.0.0
```

Recommended release title:

```text
BIP39 Prime Entropy Research v1.0.0
```

This tag should represent the first repository state intentionally declared citable and archival.

## Zenodo connection

1. Sign in to Zenodo.
2. Link the GitHub account.
3. Open the GitHub integration page.
4. Synchronize repositories if necessary.
5. Enable `BIP39-prime-entropy-research`.
6. Return to GitHub.
7. Create the `v1.0.0` release.
8. Wait for Zenodo to archive the release.
9. Open the resulting Zenodo record.
10. Record both the version DOI and, when exposed, the concept/all-versions DOI.

## DOI policy

A version DOI identifies one archived version.

A concept/all-versions DOI is useful when citing the evolving project as a whole.

For reproducibility of an exact experiment, prefer the DOI for the exact archived version.

## After DOI assignment

Update repository citation metadata and documentation with the real DOI.

Do not invent or pre-fill a DOI.

Recommended files to update:

```text
CITATION.cff
README.md
docs/CITATION_GUIDE.md
llms.txt
ai-index.json
```

Then create a subsequent release if the DOI-bearing repository state itself needs archival preservation.

## Dataset publication

Do not automatically duplicate all large generated datasets into the software record.

Software and datasets can be distinct research objects with explicit relations between their DOIs.

This is preferable when datasets are large, independently versioned, or need their own metadata.

## Permanent-record caution

Before publishing an archival release, review the repository for sensitive data.

Never archive real:

- mnemonic phrases used for assets
- private keys
- extended private keys
- raw wallet seeds
- passphrases
- API credentials
