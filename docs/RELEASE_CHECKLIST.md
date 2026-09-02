# Archival Release Checklist

## Pre-release

- [ ] `python -m pytest` passes
- [ ] GitHub Actions passes
- [ ] working tree is clean
- [ ] all intended Phase 1–9 documentation is pushed
- [ ] `CITATION.cff` is present at repository root
- [ ] repository contains no real wallet secrets
- [ ] generated mnemonic files are explicitly public experimental data
- [ ] no credentials or API tokens are present
- [ ] README security warnings are visible
- [ ] license status is accurate
- [ ] release notes describe scope and limitations

## Release identity

Recommended:

```text
Tag: v1.0.0
Title: BIP39 Prime Entropy Research v1.0.0
```

## Suggested release notes

```text
First archival research release.

This release consolidates the documented experimental architecture for BIP-39 mnemonic construction, cryptographic entropy accounting, deterministic prime-number positional mappings, absolute-coordinate experiments, structural filters, SQLite duplicate-history tracking, Bitcoin derivation utilities, reproducibility documentation, automated tests, and machine-readable dataset metadata.

Important interpretation:
- prime-number mappings do not add cryptographic entropy;
- absolute-coordinate mappings do not add cryptographic entropy;
- structural filters are deterministic selection rules;
- SQLite duplicate tracking provides local history only;
- published mnemonic datasets are public experimental data and must never be used to secure real assets.

See README.md, docs/SECURITY_MODEL.md, docs/TECHNICAL_ARCHITECTURE.md, and docs/REPRODUCIBILITY.md.
```

## Zenodo

- [ ] GitHub account linked to Zenodo
- [ ] repository enabled in Zenodo GitHub integration
- [ ] release archived successfully
- [ ] Zenodo metadata reviewed
- [ ] version DOI recorded
- [ ] concept/all-versions DOI recorded if available

## Post-DOI

- [ ] add real DOI to `CITATION.cff`
- [ ] add DOI badge/link to README if desired
- [ ] update citation guide
- [ ] update machine-readable navigation
- [ ] commit and push citation metadata changes
