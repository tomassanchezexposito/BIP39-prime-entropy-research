# Citation Guide

## Current repository citation

The repository contains `CITATION.cff` at its root.

GitHub can use this file to expose a **Cite this repository** interface and machine-readable citation metadata.

## Before a DOI exists

Cite the repository using:

- author/creator
- repository title
- version or Git commit when relevant
- GitHub repository location
- access/release date where required by the citation style

## After Zenodo archival

Prefer a DOI-based citation.

For exact reproducibility, cite the DOI of the exact archived release.

For general reference to an evolving research project, the Zenodo concept/all-versions DOI may be more appropriate.

## Software versus dataset citation

The software repository and generated datasets are conceptually different research objects.

A paper using:

- generator implementation should cite the software
- a specific generated dataset should cite that dataset record if it has its own DOI
- both should cite both objects

## CITATION.cff fields

Important fields include:

```text
cff-version
message
title
authors
version
date-released
url
doi
```

Only add `doi` after a DOI has actually been assigned.

Do not invent ORCID identifiers.

Do not infer a license.

## Preferred citation

If a peer-reviewed paper or formal technical report later becomes the canonical scholarly description of this research, `CITATION.cff` can use `preferred-citation` to point users toward that work while still describing the software repository.
