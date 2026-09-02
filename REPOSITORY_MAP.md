# Repository Map

## Purpose

This file is the compact directory map for humans, crawlers, code assistants, and AI retrieval systems.

## Root

| Path | Purpose |
|---|---|
| `README.md` | Canonical overview and primary entry point |
| `llms.txt` | AI/agent-oriented navigation |
| `ARCHITECTURE.md` | Conceptual architecture |
| `REPOSITORY_MAP.md` | This navigation map |
| `CITATION.cff` | Citation metadata |
| `LICENSE` | MIT License |
| `DISCLAIMER.md` | Security and usage limitations |
| `CONTRIBUTING.md` | Contribution rules |
| `CHANGELOG.md` | Project history |
| `REFERENCES.md` | Standards and authoritative references |
| `SOURCE_AUDIT.md` | Source provenance / traceability |
| `ai-index.json` | Machine-readable project discovery index |
| `pyproject.toml` | Python/test configuration |

## `src/`

Historical Python research implementations.

Read `docs/MODULE_MAP.md` before interpreting filenames as current architecture.

Important families include:

- finite 12-word generators
- reinforced-filter generators
- absolute/infinite-coordinate generators
- 24-word branch
- V2.4/V2.5/V2.6/V2.7 batch generators
- V2.7 large-database compatibility fix
- forward Bitcoin address derivation utilities
- finite file-based verification utilities

## `tests/`

Automated deterministic tests.

Primary current test module:

`tests/test_v27_core.py`

Run:

```bash
python -m pytest
```

## `scripts/`

Repository maintenance and dataset tooling.

| Script | Purpose |
|---|---|
| `generate_sha256s.py` | Dataset file integrity hashes |
| `build_dataset_package.py` | Dataset card, metadata, JSON-LD, hashes |
| `build_datasets_index.py` | Repository-wide dataset discovery index |

## `generated_phrases/`

Public experimental mnemonic datasets.

Start with:

`generated_phrases/README.md`

Machine discovery:

`generated_phrases/DATASETS_INDEX.json`

Preferred per-dataset evidence:

```text
DATASET_CARD.md
metadata.json
dataset.jsonld
MANIFIESTO.tsv
SHA256SUMS.txt
```

Raw `*.txt` files should be read only after metadata.

## `docs/` — research

| File | Purpose |
|---|---|
| `RESEARCH_SUMMARY.md` | Research scope, claims, and non-claims |
| `REPRODUCIBILITY.md` | Reproduction protocol |
| `VERSION_MATRIX.md` | Historical implementation evolution |
| `SCHOLARLY_DISCOVERY.md` | Scholarly discovery strategy |
| `ZENODO_PUBLICATION.md` | Zenodo archival publication workflow |
| `CITATION_GUIDE.md` | Citation and DOI guidance |

## `docs/` — architecture

| File | Purpose |
|---|---|
| `TECHNICAL_ARCHITECTURE.md` | Software architecture |
| `MODULE_MAP.md` | Semantic source-file map |
| `DATA_FLOW.md` | End-to-end candidate/data flow |
| `API_REFERENCE.md` | Important function contracts |
| `BIP39_PIPELINE.md` | BIP-39 construction |
| `PRIME_COORDINATE_MODEL.md` | Prime/local/absolute coordinate model |
| `SQLITE_MODEL.md` | Duplicate-history persistence |
| `AI_CODE_READING_GUIDE.md` | AI-specific evidence and reading order |

## `docs/` — quality and safety

| File | Purpose |
|---|---|
| `SECURITY_MODEL.md` | Security boundaries |
| `CODE_QUALITY.md` | Code-quality policy |
| `GLOSSARY.md` | Canonical terminology |

## `docs/` — datasets

| File | Purpose |
|---|---|
| `DATASET_DISCOVERY.md` | Dataset discovery rules |
| `dataset_metadata.schema.json` | Metadata JSON Schema |
| `DATASET_CARD_TEMPLATE.md` | Dataset-card template |
| `DATASET_CARD_TEMPLATE_V2.md` | Extended dataset-card template |
| `schemaorg_dataset.template.json` | schema.org Dataset template |
| `HUGGINGFACE_DATASET_CARD_TEMPLATE.md` | Hugging Face preparation |
| `HUGGINGFACE_PUBLISHING.md` | Hugging Face publication guidance |

## `docs/` — dissemination

| File | Purpose |
|---|---|
| `DISSEMINATION_STRATEGY.md` | External dissemination strategy |
| `ZENODO_COMMUNITIES_GUIDE.md` | Zenodo Communities submission guidance |
| `OPENAIRE_GUIDE.md` | OpenAIRE discovery guidance |
| `INSTITUTIONAL_OUTREACH.md` | Institutional outreach guidance |
| `PHASE_10_ACTION_PLAN.md` | External dissemination action plan |

## `docs/reports/`

Long-form project history and publication reports.

| File | Purpose |
|---|---|
| `PROJECT_PUBLICATION_AND_DISSEMINATION_REPORT_EN.md` | Complete publication, optimization, archival, citation and dissemination history of the project |

This report records the technical stabilization, GitHub publication process, Git LFS setup, testing and CI, dataset metadata, reproducibility work, AI-oriented navigation, Zenodo DOI publication, MIT licensing, and the external dissemination plan.

## `outreach/`

Reusable communication material for external dissemination.

| File | Purpose |
|---|---|
| `ACADEMIC_CONTACT_TEMPLATE.md` | Academic and research-group outreach template |
| `TECHNICAL_COMMUNITY_POST.md` | Technical community publication template |
| `LINKEDIN_POST.md` | Professional dissemination draft |

## `.github/`

GitHub automation and collaboration metadata.

Contains:

- GitHub Actions tests
- issue forms
- pull-request template

## Recommended reading paths

### Understand the project

```text
README
→ RESEARCH_SUMMARY
→ ARCHITECTURE
→ TECHNICAL_ARCHITECTURE
```

### Understand how the repository was published and optimized

```text
README
→ docs/reports/PROJECT_PUBLICATION_AND_DISSEMINATION_REPORT_EN.md
→ REPOSITORY_MAP
→ VERSION_MATRIX
```

### Analyze cryptographic construction

```text
BIP39_PIPELINE
→ SECURITY_MODEL
→ tests
→ exact source version
```

### Analyze prime mapping

```text
PRIME_COORDINATE_MODEL
→ DATA_FLOW
→ exact source version
```

### Analyze a dataset

```text
DATASETS_INDEX.json
→ DATASET_CARD.md
→ metadata.json
→ dataset.jsonld
→ MANIFIESTO.tsv
→ SHA256SUMS.txt
→ raw TXT
```

### Reproduce results

```text
REPRODUCIBILITY
→ VERSION_MATRIX
→ exact source
→ tests
→ manifest/hashes
```

### Review publication and dissemination history

```text
PROJECT_PUBLICATION_AND_DISSEMINATION_REPORT_EN.md
→ ZENODO_PUBLICATION.md
→ CITATION_GUIDE.md
→ DISSEMINATION_STRATEGY.md
```

## Persistent research identity

Repository:

`https://github.com/tomassanchezexposito/BIP39-prime-entropy-research`

Archived software release:

`v1.1.0`

Zenodo DOI:

`10.5281/zenodo.22257814`

License:

`MIT`

## Interpretation invariant

Prime labels, absolute coordinates, structural filters, SQLite duplicate history, and metadata are deterministic mechanisms and must not be counted as cryptographic entropy.
