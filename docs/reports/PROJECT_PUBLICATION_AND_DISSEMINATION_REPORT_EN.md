# Project Publication, Optimization, Indexability and Dissemination Report

## Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research

**Repository:**  
https://github.com/tomassanchezexposito/BIP39-prime-entropy-research

**Archived software release:**  
v1.1.0

**Zenodo DOI:**  
https://doi.org/10.5281/zenodo.22257814

**License:**  
MIT

**Author:**  
Tomás Sánchez Exposito

**Date:**  
September 2026

---

## 1. Executive summary

This report documents the work carried out to transform the `BIP39-prime-entropy-research` project from a technical collection of generators, documentation, and datasets into a public research repository that is structured, reproducible, citable, understandable by both humans and AI systems, and prepared for technical, academic, and institutional dissemination.

The work went significantly beyond uploading source code to GitHub. It included:

- validation and stabilization of the main generator;
- diagnosis and correction of large historical SQLite database performance issues;
- repository architecture and organization;
- Git LFS for large generated datasets;
- scientific and technical documentation;
- explicit security interpretation boundaries;
- automated tests;
- GitHub Actions continuous integration;
- dataset metadata and integrity files;
- machine-readable dataset discovery;
- AI-oriented repository navigation;
- technical SEO and discoverability;
- `CITATION.cff`;
- Zenodo archival publication;
- DOI assignment;
- adoption of the MIT License;
- and an external dissemination strategy.

The resulting repository now functions as a public research infrastructure rather than as a simple code archive.

### 1.1 Core scientific interpretation rules

The repository deliberately preserves the following distinctions:

- The mapping between BIP-39 positions and prime numbers is deterministic and **does not add cryptographic entropy**.
- Absolute-coordinate or extended-coordinate transforms are deterministic and **do not add entropy**.
- Structural filters reject candidates according to deterministic rules and **do not generate randomness**.
- The BIP-39 checksum is deterministic and derived from SHA-256.
- In the documented V2.7 12-word design with a fixed and known first BIP-39 position, 11 entropy bits are fixed and the remaining 117 entropy bits are generated through Python `secrets` / the operating-system CSPRNG.
- SQLite stores a local history of phrase hashes and reduces local re-emission; it does **not** prove global uniqueness.
- Mnemonics published in public datasets are experimental public data and must never be used to secure real assets.

### 1.2 Main milestones reached

| Milestone | Result |
|---|---|
| Public GitHub repository | Structured repository with documentation, releases, datasets and Git LFS |
| Technical validation | Deterministic tests and large generation validation |
| Reproducibility | Manifests, hashes, dataset cards, metadata and reproduction guidance |
| AI discoverability | `llms.txt`, `ai-index.json`, repository map and AI reading guidance |
| Automation | GitHub Actions running the test suite across multiple Python versions |
| Citation | GitHub citation metadata through `CITATION.cff` |
| Archival publication | Zenodo software record |
| DOI | `10.5281/zenodo.22257814` |
| License | MIT |
| Dissemination | Structured external outreach plan |

---

## 2. Chronological work map

The publication and optimization process was divided into ten phases, preceded by a technical stabilization stage.

| Stage | Main objective |
|---|---|
| Technical baseline | Diagnose V2.7 / SQLite behavior and validate large-scale generation |
| Phase 1 | GitHub publication, repository structure, Git LFS, datasets and initial release |
| Phase 2 | Code quality, security model, glossary and automated tests |
| Phase 3 | Dataset metadata, integrity and traceability |
| Phase 4 | GitHub Actions and collaboration templates |
| Phase 5 | Scientific summary, reproducibility and version matrix |
| Phase 6 | Advanced dataset discovery and AI indexing |
| Phase 7 | Deep technical architecture and data-flow documentation |
| Phase 8 | Technical SEO, discoverability and machine-readable navigation |
| Phase 9 | Zenodo, DOI, citation and MIT licensing |
| Phase 10 | External academic, technical, institutional and professional dissemination |

---

## 3. Technical baseline before publication

### 3.1 V2.5 / V2.6 / V2.7 startup issue

Before optimizing the public repository, a major performance issue was investigated.

V2.5, V2.6 and V2.7 could appear to freeze before writing the first output file when they reused a very large historical SQLite database.

These versions shared the same application identity:

```python
APP_NAME = "GeneradorPrimosPalabrasV25TurboMultiCPU"
```

This meant they reused the same application-data directory and historical database.

V2.4 used a different application identity and therefore a separate and much smaller database, which explained why V2.4 could start normally while later versions appeared stalled.

The root cause was a startup query equivalent to:

```sql
SELECT COUNT(*) FROM generated
```

against a very large historical table.

Large database-related files were observed in the application data directory, including database/WAL/SHM state reaching tens of gigabytes.

A controlled test was performed by temporarily renaming the historical application-data directory and allowing the generator to create a fresh database. V2.5 then generated 10 groups immediately, in roughly 0.31 seconds, confirming that the historical database size—not the generation logic—was responsible for the apparent freeze.

### 3.2 V2.7 large-database fix

A V2.7 compatibility fix was created that preserved the historical database while avoiding a full-table startup count.

The key helper became:

```python
def db_generated_count_fast(con):
    row = con.execute(
        "SELECT COALESCE(MAX(rowid), 0) FROM generated"
    ).fetchone()
    return int(row[0] or 0)
```

The final count was also changed so that the application no longer executed another expensive `COUNT(*)` after the generation session. Instead, the result was derived from the initial count plus the number of newly generated rows.

The historical `APP_NAME` was deliberately preserved so that the fix continued to use the existing database rather than silently creating a new history.

**Technical caveat:** `MAX(rowid)` is exact under the normal append-only behavior of this application. If rows were manually deleted, it could overstate the actual row count. The application itself does not delete rows.

### 3.3 Validation tests

The fix and generator behavior were validated with both small and large sessions.

#### Small test

- Range: `221 → 221`
- 10 groups
- 10 output groups produced
- generation completed successfully
- generated mnemonics were unique within the test
- the last mnemonic was independently reconstructed from BIP-39 indexes
- entropy and checksum were verified as internally coherent

#### Large test

- Range: `221 → 222`
- 1,000,000 groups per value
- 2,000,000 groups total
- generation time: approximately `00:12:10`
- final prime-processing stage: approximately `00:05:24`
- total time: approximately `00:17:35`
- generation throughput: approximately 2,740 groups/second
- end-to-end throughput including final prime processing: approximately 1,896 groups/second
- SQLite historical count increased exactly by 2,000,000
- manifest continuity was correct
- both values were marked `COMPLETO`

These tests provided a validated technical baseline before publication.

---

## 4. Phase 1 — GitHub publication and large-file management

### 4.1 Public repository

The project was published at:

```text
https://github.com/tomassanchezexposito/BIP39-prime-entropy-research
```

The repository evolved toward a conventional research-software structure:

```text
.
├── README.md
├── llms.txt
├── ARCHITECTURE.md
├── REPOSITORY_MAP.md
├── CITATION.cff
├── LICENSE
├── DISCLAIMER.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── REFERENCES.md
├── SOURCE_AUDIT.md
├── pyproject.toml
├── src/
├── tests/
├── scripts/
├── docs/
├── outreach/
└── generated_phrases/
```

### 4.2 Git LFS for generated datasets

Generated mnemonic text files were too large and too numerous to manage efficiently as normal Git blobs.

Git LFS was configured for generated phrase TXT files:

```gitattributes
generated_phrases/**/*.txt
generated_phrases/*.txt
```

Metadata files such as README files, manifests, JSON metadata and status documents were kept outside LFS whenever appropriate so they remained lightweight and directly readable on GitHub.

The LFS workflow was verified using:

```bash
git lfs ls-files
git lfs prune --dry-run
git lfs prune
```

Manual deletion of `.git/lfs/objects` was intentionally avoided.

### 4.3 Metadata-first repository strategy

A major design decision emerged at this stage:

> AI systems, researchers and reviewers should not need to read millions of raw mnemonic lines in order to understand a dataset.

This principle later motivated:

- `DATASET_CARD.md`
- `metadata.json`
- `dataset.jsonld`
- `SHA256SUMS.txt`
- `DATASETS_INDEX.json`
- dataset discovery documentation
- and AI navigation files

### 4.4 GitHub topics and social presentation

A technical topic strategy was prepared using established terms such as:

```text
bip39
bitcoin
bitcoin-wallet
cryptography
entropy
mnemonic
seed-phrase
hd-wallet
bip84
native-segwit
bech32
secp256k1
prime-numbers
number-theory
python
security-research
reproducibility
dataset
sha256
blockchain
```

Terms suggesting seed cracking, broken cryptography or unsupported entropy claims were intentionally avoided.

A social-preview graphic was also prepared for the repository.

### 4.5 Initial release

An initial public release, `v1.0.0`, was created:

```text
Architecture of Infinity — Initial Public Research Release
```

A later archival release, `v1.1.0`, was created after substantial additional infrastructure and documentation had been added.

---

## 5. Phase 2 — Code quality, security model and tests

Phase 2 introduced a minimum research-software quality layer.

Files added included:

| File | Purpose |
|---|---|
| `docs/CODE_QUALITY.md` | Code-quality policy, comments, docstrings and historical-code handling |
| `docs/GLOSSARY.md` | Canonical terminology |
| `docs/SECURITY_MODEL.md` | Security boundaries and interpretation |
| `pyproject.toml` | Python / pytest configuration |
| `tests/README.md` | Testing instructions and scope |
| `tests/test_v27_core.py` | Deterministic V2.7 core tests |

### 5.1 Tested behavior

Tests covered:

- `local_position`
- position wrapping in the `1..2048` space
- invalid absolute-position handling
- `block_number`
- BIP-39 entropy/checksum construction
- zero-entropy deterministic vectors

An initial Python 3.14 loading issue appeared because the dynamically imported historical module was not inserted into `sys.modules` before `exec_module`.

The test loader was corrected to register the module first.

Final result:

```text
14 passed
```

A passing test suite was explicitly documented as evidence for tested deterministic behavior, not as a complete cryptographic audit.

---

## 6. Phase 3 — Dataset metadata, integrity and traceability

Phase 3 transformed generated output directories into documented research datasets.

Files included:

| File | Purpose |
|---|---|
| `generated_phrases/README.md` | Dataset conventions and warnings |
| `docs/DATASET_CARD_TEMPLATE.md` | Dataset-card template |
| `docs/metadata.schema.json` | Metadata schema |
| `docs/metadata.example.json` | Metadata example |
| `docs/SHA256SUMS_README.md` | Integrity documentation |
| `scripts/generate_sha256s.py` | SHA-256 integrity generation |

### 6.1 Forty-million-group dataset

The dataset:

```text
millon_441_a_480_20260830_171221
```

was used as a fully documented example.

Its manifest contained:

- values 441 through 480;
- 40 manifest rows;
- 1,000,000 groups per value;
- 40,000,000 groups total;
- continuous global group numbering;
- all rows marked `COMPLETO`.

A dataset-specific:

```text
DATASET_CARD.md
metadata.json
SHA256SUMS.txt
```

was prepared.

The documentation explicitly recorded:

- 12-word BIP-39 format;
- 128-bit entropy;
- 11 fixed bits from the known first position;
- 117 CSPRNG-generated bits;
- 4 checksum bits;
- deterministic prime mapping;
- deterministic structural filters;
- local SQLite duplicate scope.

`SHA256SUMS.txt` was documented as an integrity mechanism, not as a cryptographic security or uniqueness proof.

---

## 7. Phase 4 — GitHub Actions and collaboration infrastructure

Phase 4 added continuous integration and contribution templates.

Files included:

| File | Purpose |
|---|---|
| `CONTRIBUTING.md` | Contribution and testing rules |
| `.github/workflows/tests.yml` | Automated test workflow |
| `.github/ISSUE_TEMPLATE/bug_report.yml` | Bug reports |
| `.github/ISSUE_TEMPLATE/research_question.yml` | Research questions |
| `.github/ISSUE_TEMPLATE/reproducibility_report.yml` | Reproducibility reports |
| `.github/pull_request_template.md` | Pull request template |

The workflow ran on:

```text
windows-latest
Python 3.10
Python 3.12
Python 3.14
```

and executed:

```bash
python -m pytest
```

All three matrix jobs completed successfully.

Warnings related to Node.js versions in GitHub Actions dependencies were noted as action-maintenance warnings, not test failures.

---

## 8. Phase 5 — Scientific summary and reproducibility documentation

Phase 5 added:

| File | Purpose |
|---|---|
| `docs/RESEARCH_SUMMARY.md` | Research scope, supported claims and non-claims |
| `docs/REPRODUCIBILITY.md` | Reproduction protocol |
| `docs/VERSION_MATRIX.md` | Historical implementation evolution |

The reproducibility guide established that a meaningful experiment should record at least:

- exact Git commit or release;
- exact source file/version;
- Python version;
- operating system;
- generation parameters;
- filter version;
- SQLite history state;
- manifest;
- integrity hashes.

The version matrix prevented readers from incorrectly assuming that every historical generator implemented the same model.

---

## 9. Phase 6 — Advanced dataset discovery and AI indexing

Phase 6 automated dataset metadata generation and discovery.

Files included:

| File | Purpose |
|---|---|
| `scripts/build_dataset_package.py` | Builds dataset card, metadata, JSON-LD and hashes |
| `scripts/build_datasets_index.py` | Builds repository-wide dataset index |
| `docs/dataset_metadata.schema.json` | Machine-readable metadata schema |
| `docs/DATASET_CARD_TEMPLATE_V2.md` | Extended dataset-card template |
| `docs/HUGGINGFACE_DATASET_CARD_TEMPLATE.md` | Hugging Face-oriented dataset card |
| `docs/HUGGINGFACE_PUBLISHING.md` | Publication guidance |
| `docs/DATASET_DISCOVERY.md` | Dataset evidence hierarchy |
| `docs/schemaorg_dataset.template.json` | schema.org Dataset template |
| `generated_phrases/DATASETS_INDEX.json` | Repository-wide dataset index |

### 9.1 Real execution

The dataset package builder was run against the 441–480 dataset.

The expected results were obtained:

```text
Manifest rows: 40
Total groups: 40000000
Inventory files: 41
```

The 41 inventoried files corresponded to the 40 TXT outputs plus the manifest.

The repository-wide index successfully recognized the dataset.

The intended discovery order became:

```text
DATASETS_INDEX.json
→ DATASET_CARD.md
→ metadata.json
→ dataset.jsonld
→ MANIFIESTO.tsv
→ SHA256SUMS.txt
→ raw TXT files
```

This made the project substantially easier to interpret by both humans and automated systems.

---

## 10. Phase 7 — Deep technical architecture

Phase 7 documented the software architecture in a way that does not require reverse-engineering historical monolithic scripts.

Files added:

| File | Purpose |
|---|---|
| `docs/TECHNICAL_ARCHITECTURE.md` | Software layers and dependency direction |
| `docs/MODULE_MAP.md` | Semantic mapping of historical source files |
| `docs/DATA_FLOW.md` | End-to-end candidate/data flow |
| `docs/API_REFERENCE.md` | Important functions and semantic contracts |
| `docs/SQLITE_MODEL.md` | Persistence and duplicate history |
| `docs/BIP39_PIPELINE.md` | Entropy, checksum and indexes |
| `docs/PRIME_COORDINATE_MODEL.md` | Prime/local/absolute coordinate interpretation |
| `docs/AI_CODE_READING_GUIDE.md` | AI reading order and evidence hierarchy |

### 10.1 Consolidated conceptual flow

The architecture was described approximately as:

```text
OS CSPRNG / Python secrets
        ↓
entropy construction
        ↓
SHA-256 checksum
        ↓
11-bit BIP-39 indexes
        ↓
BIP-39 words
        ↓
deterministic structural filter
        ↓
local positions 1..2048
        ↓
odd-prime ordinal labels
        ↓
absolute coordinates
        ↓
phrase SHA-256 hash → SQLite
        ↓
batch / manifest / TXT output
        ↓
metadata / JSON-LD / SHA256SUMS
```

The documentation also proposed a future modular architecture separating:

- core mathematics;
- BIP-39;
- filters;
- persistence;
- batch orchestration;
- datasets;
- GUI.

Historical files remain preserved for traceability.

---

## 11. Phase 8 — Technical SEO, discoverability and AI navigation

Phase 8 optimized the repository for semantic discovery rather than keyword stuffing.

Key files:

| File | Purpose |
|---|---|
| `README.md` | Canonical project overview and navigation |
| `llms.txt` | Compact AI/agent navigation |
| `REPOSITORY_MAP.md` | Directory and evidence map |
| `ai-index.json` | Structured AI-oriented index |
| `docs/DISCOVERY_METADATA.md` | Topics, description and search vocabulary |

### 11.1 AI navigation

The intended reading flow became:

```text
repository
   ↓
llms.txt / ai-index.json
   ↓
README
   ↓
RESEARCH_SUMMARY
   ↓
TECHNICAL_ARCHITECTURE
   ↓
BIP39 / Prime / SQLite models
   ↓
tests + exact source version
   ↓
DATASETS_INDEX
   ↓
dataset metadata
   ↓
large raw data
```

This structure improves machine readability and retrieval but does not guarantee that any particular search engine or AI provider will crawl, index, rank, train on or cite the repository.

---

## 12. Phase 9 — Zenodo, DOI, citation and MIT License

### 12.1 Archival publication preparation

The following files were added:

| File | Purpose |
|---|---|
| `docs/ZENODO_PUBLICATION.md` | Zenodo workflow and DOI policy |
| `docs/CITATION_GUIDE.md` | Citation guidance |
| `docs/RELEASE_CHECKLIST.md` | Archival release checklist |
| `docs/SCHOLARLY_DISCOVERY.md` | Scholarly discovery strategy |

### 12.2 GitHub–Zenodo connection

Zenodo was connected to the GitHub account and the specific repository:

```text
tomassanchezexposito/BIP39-prime-entropy-research
```

was enabled in the GitHub integration.

Because the existing `v1.0.0` release had been created before Zenodo was enabled, that historical release was not rewritten or replaced.

Instead, a new archival release was created:

```text
Tag: v1.1.0
Target: main
Title: Architecture of Infinity — Research Infrastructure Release v1.1.0
```

### 12.3 DOI assignment

Zenodo successfully archived `v1.1.0` as software.

The assigned DOI is:

```text
10.5281/zenodo.22257814
```

Persistent URL:

```text
https://doi.org/10.5281/zenodo.22257814
```

### 12.4 License decision

Zenodo initially showed Creative Commons Attribution 4.0 International as the record license.

Because the project goal was maximum diffusion and software reuse, the license was deliberately changed to:

```text
MIT License
```

A repository-level `LICENSE` file was then added and the following files were aligned with the MIT decision and DOI:

```text
LICENSE
CITATION.cff
README.md
llms.txt
ai-index.json
docs/CITATION_GUIDE.md
```

The `v1.1.0` tag was not rewritten after archival. Post-release metadata changes were committed to `main` and should belong to a later versioned release rather than altering the historical archived snapshot.

### 12.5 Recommended citation

```text
Sánchez Exposito, T. (2026).
Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research
(Version v1.1.0) [Computer software].
Zenodo.
https://doi.org/10.5281/zenodo.22257814
```

---

## 13. Phase 10 — External dissemination strategy

Once the repository infrastructure was complete, Phase 10 shifted from internal optimization to external dissemination.

Files added:

| File | Purpose |
|---|---|
| `docs/DISSEMINATION_STRATEGY.md` | Overall dissemination strategy |
| `docs/ZENODO_COMMUNITIES_GUIDE.md` | Zenodo Community submission guidance |
| `docs/OPENAIRE_GUIDE.md` | OpenAIRE discovery checks |
| `docs/INSTITUTIONAL_OUTREACH.md` | Institutional outreach guidance |
| `docs/PHASE_10_ACTION_PLAN.md` | Operational action plan |
| `outreach/ACADEMIC_CONTACT_TEMPLATE.md` | Academic contact template |
| `outreach/TECHNICAL_COMMUNITY_POST.md` | Technical community post |
| `outreach/LINKEDIN_POST.md` | Professional dissemination draft |

### 13.1 Recommended dissemination order

1. Zenodo Communities
2. OpenAIRE
3. Banco de España innovation channel
4. University and research groups
5. Technical communities and GitHub discussion
6. LinkedIn and professional visibility

The emphasis is on technical review, reproducibility and legitimate scholarly visibility rather than superficial reach.

---

## 14. Security model and publication boundaries

The project maintains a clear distinction between legitimate experimental generation / representation research and credential recovery.

Appropriate public research activities include:

- generating experimental BIP-39 mnemonics;
- validating BIP-39 checksums;
- mapping BIP-39 indexes to prime labels;
- deriving public Bitcoin addresses from known test mnemonics;
- publishing public experimental datasets;
- documenting deterministic filters;
- measuring generator performance;
- verifying file integrity;
- inspecting public blockchain data.

The project should not be reframed as a tool for discovering unknown wallet seed phrases from a target Bitcoin address through massive candidate exploration.

### 14.1 Sensitive data rules

Never publish real:

- funded-wallet mnemonic phrases;
- private keys;
- xprv values;
- raw wallet seeds;
- BIP-39 passphrases;
- API credentials.

Any mnemonic intentionally published in a public dataset is compromised by definition and must never secure real assets.

---

## 15. Canonical terminology

| Term | Correct interpretation |
|---|---|
| Entropy | Random input bits produced by the documented CSPRNG |
| Checksum | Deterministic SHA-256-derived BIP-39 checksum bits |
| BIP-39 index | Value in `0..2047` |
| Local position | Value in `1..2048`, equal to index + 1 |
| Prime label | Deterministic odd-prime ordinal representation |
| Absolute position | Extended deterministic coordinate |
| Structural filter | Deterministic candidate-rejection rule |
| SQLite duplicate history | Local phrase-hash history |
| Manifest | Generation/file accounting and traceability |
| `SHA256SUMS.txt` | File-integrity verification |

---

## 16. Final repository state

A representative final structure is:

```text
BIP39-prime-entropy-research/
├── .github/
│   ├── workflows/tests.yml
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── docs/
│   ├── AI_CODE_READING_GUIDE.md
│   ├── API_REFERENCE.md
│   ├── BIP39_PIPELINE.md
│   ├── CITATION_GUIDE.md
│   ├── CODE_QUALITY.md
│   ├── DATA_FLOW.md
│   ├── DATASET_DISCOVERY.md
│   ├── DISCOVERY_METADATA.md
│   ├── DISSEMINATION_STRATEGY.md
│   ├── GLOSSARY.md
│   ├── INSTITUTIONAL_OUTREACH.md
│   ├── MODULE_MAP.md
│   ├── OPENAIRE_GUIDE.md
│   ├── PHASE_10_ACTION_PLAN.md
│   ├── PRIME_COORDINATE_MODEL.md
│   ├── RELEASE_CHECKLIST.md
│   ├── REPRODUCIBILITY.md
│   ├── RESEARCH_SUMMARY.md
│   ├── SCHOLARLY_DISCOVERY.md
│   ├── SECURITY_MODEL.md
│   ├── SQLITE_MODEL.md
│   ├── TECHNICAL_ARCHITECTURE.md
│   ├── VERSION_MATRIX.md
│   ├── ZENODO_COMMUNITIES_GUIDE.md
│   ├── ZENODO_PUBLICATION.md
│   └── dataset templates / schemas
├── generated_phrases/
│   ├── README.md
│   ├── DATASETS_INDEX.json
│   └── <datasets>/
│       ├── MANIFIESTO.tsv
│       ├── DATASET_CARD.md
│       ├── metadata.json
│       ├── dataset.jsonld
│       ├── SHA256SUMS.txt
│       └── *.txt
├── outreach/
│   ├── ACADEMIC_CONTACT_TEMPLATE.md
│   ├── TECHNICAL_COMMUNITY_POST.md
│   └── LINKEDIN_POST.md
├── scripts/
│   ├── build_dataset_package.py
│   ├── build_datasets_index.py
│   └── generate_sha256s.py
├── src/
├── tests/
│   ├── README.md
│   └── test_v27_core.py
├── LICENSE
├── CITATION.cff
├── README.md
├── llms.txt
├── ai-index.json
├── ARCHITECTURE.md
├── REPOSITORY_MAP.md
├── CONTRIBUTING.md
├── DISCLAIMER.md
├── CHANGELOG.md
├── REFERENCES.md
├── SOURCE_AUDIT.md
└── pyproject.toml
```

---

## 17. Key commands used

| Operation | Command |
|---|---|
| Run tests | `python -m pytest` |
| Build dataset package | `python scripts/build_dataset_package.py generated_phrases/<dataset>` |
| Build dataset index | `python scripts/build_datasets_index.py` |
| Generate SHA-256 hashes | `python scripts/generate_sha256s.py generated_phrases/<dataset>` |
| List Git LFS objects | `git lfs ls-files` |
| Preview LFS pruning | `git lfs prune --dry-run` |
| Prune safe local LFS objects | `git lfs prune` |

---

## 18. Main design decisions

| Decision | Reason |
|---|---|
| Preserve historical scripts | Maintain traceability rather than rewriting history |
| Use Git LFS for large TXT files | Avoid inflating normal Git history |
| Metadata-first dataset navigation | Make datasets understandable without reading raw millions of lines |
| Do not invent a license | License was left unspecified until an explicit decision was made |
| Adopt MIT | Maximize reuse and dissemination |
| Use `CITATION.cff` | Provide GitHub- and machine-readable citation metadata |
| Create `v1.1.0` after Zenodo activation | Preserve `v1.0.0` history and archive the current state |
| Add the DOI only after assignment | Avoid fabricated or premature metadata |
| Preserve non-claims | Prevent deterministic prime/filter mechanisms from being misrepresented as entropy |
| Use tests + exact source + manifest + hashes | Build a reproducible evidence chain |

---

## 19. Problems encountered and resolutions

| Problem | Cause | Resolution |
|---|---|---|
| V2.5–V2.7 appeared frozen | Huge historical SQLite database and `COUNT(*)` | Fast count strategy based on `MAX(rowid)` |
| V2.4 behaved differently | Separate application-data identity/database | Difference identified and documented |
| Python 3.14 dynamic test load failed | Module not registered in `sys.modules` before execution | Loader corrected |
| Large TXT files were unsuitable for normal Git | File size and volume | Git LFS |
| Prime/filter terminology could be misread as security | Ambiguous interpretation risk | Security model, glossary, README, architecture and AI guidance |
| Zenodo defaulted to CC BY 4.0 | Default record licensing behavior | Explicit change to MIT |
| `v1.0.0` predated Zenodo activation | No reason to assume retroactive archival | New `v1.1.0` release created after integration was enabled |

---

## 20. Public identity and citation

### Repository

```text
https://github.com/tomassanchezexposito/BIP39-prime-entropy-research
```

### Archived software release

```text
v1.1.0
```

### DOI

```text
https://doi.org/10.5281/zenodo.22257814
```

### License

```text
MIT License
```

### Recommended citation

```text
Sánchez Exposito, T. (2026).
Architecture of Infinity: Prime Coordinates and BIP-39 Mnemonic Research
(Version v1.1.0) [Computer software].
Zenodo.
https://doi.org/10.5281/zenodo.22257814
```

---

## 21. Dissemination plan from this point forward

The repository is now sufficiently prepared for external dissemination.

Recommended order:

| Priority | Action | Intended outcome |
|---|---|---|
| 1 | Zenodo Communities | Thematic curation and discoverability |
| 2 | OpenAIRE | Scholarly discovery by DOI and metadata |
| 3 | Banco de España | Innovation-oriented institutional guidance |
| 4 | Universities and research groups | Independent technical review and reproducibility |
| 5 | Technical communities | Issues, criticism and replication reports |
| 6 | LinkedIn / web | Professional visibility and backlinks |

The highest-value future result would be an independent reproduction, serious technical critique, or scholarly citation rather than a large number of social-media impressions.

---

## 22. Recommended next scientific milestone

The next major research artifact should be a formal technical manuscript or preprint, separate from the software repository, with its own persistent identifier.

A suggested structure is:

```text
Abstract
Research question
Background: BIP-39 and entropy
Prime-coordinate representation
Finite and absolute coordinate models
Structural filters
Implementation
Reproducibility
Experimental results
Security interpretation
Limitations
Discussion
Conclusion
References
```

The software, manuscript and datasets should remain distinct but related research objects.

---

## 23. Maintenance checklist

Future maintenance should preserve the following practices:

- do not rewrite archived tags;
- create new versioned releases;
- update `CITATION.cff`, README, `llms.txt` and `ai-index.json` when archival version metadata changes;
- keep Zenodo and GitHub license information consistent;
- run tests before releases;
- keep GitHub Actions green;
- generate manifests, metadata and `SHA256SUMS.txt` for new datasets;
- rebuild `DATASETS_INDEX.json`;
- record generation parameters and SQLite history state;
- never publish real secrets;
- retain the explicit non-claims regarding entropy;
- prioritize reproducibility and technical review over superficial reach.

---

## 24. Conclusion

The publication process transformed the project into a substantially more mature research infrastructure.

The principal achievement is not simply the number of files added. It is the creation of a coherent chain connecting:

```text
implementation
→ tests
→ documentation
→ datasets
→ metadata
→ reproducibility
→ citation
→ archival publication
→ dissemination
```

The repository can now be approached from multiple levels:

- a general visitor can start with `README.md`;
- an AI system can start with `llms.txt` or `ai-index.json`;
- a technical reviewer can follow architecture → tests → exact source;
- a dataset researcher can follow `DATASETS_INDEX.json` → metadata → manifest → hashes;
- and a scholarly publication can cite the persistent Zenodo DOI.

The adoption of the MIT License supports the goal of maximum reuse and dissemination, while the Zenodo DOI provides persistent identity and citation.

The project is therefore ready to move from internal optimization toward external review, reproducibility, discussion and scholarly visibility.
