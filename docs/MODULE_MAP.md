# Module Map

## Purpose

This document maps the main historical source files and supporting tooling to their responsibilities.

## Historical generators

### `src/generador_12_palabras.py`

Role:

- initial finite 12-word research generator
- finite BIP-39 positional model
- early prime-position representation

Interpretation:

- historical baseline
- deterministic prime labels do not add entropy

### `src/generador_v3_finita_filtro_total_reforzado.py`

Role:

- finite-domain generator
- strengthened deterministic structural filtering

Interpretation:

- filter changes acceptance behavior
- filter does not create randomness

### `src/generador_v3_infinita_filtro_total_reforzado.py`

Role:

- infinite / absolute-coordinate variant
- local-to-absolute positional research

Interpretation:

- coordinate extension is deterministic

### `src/generador_24_palabras_infinita_filtro_lineal_total.py`

Role:

- 24-word BIP-39 research branch
- expanded entropy-length experiment

### `src/Generador_V2_4_MultiGrupos.py`

Role:

- sequential multi-group generation
- SQLite duplicate tracking
- file export

### `src/Generador_V2_6_AUTO_Turbo_Rango.py`

Role:

- automatic generation by value range
- groups-per-value and groups-per-file controls
- optimized batch flow

### `src/Generador_V2_7_AUTO_Turbo_Cronometros.py`

Role:

- automatic ranged generation
- SQLite duplicate hashes
- worker configuration
- progress events
- heartbeat
- separate generation and final-prime timing

Key pure functions documented by tests include:

- `local_position`
- `block_number`
- `indexes_from_entropy`

### `src/Generador_V2_7_AUTO_Turbo_Cronometros_FIX_DB_GRANDE.py`

Role:

- V2.7 compatibility fix for very large historical SQLite databases
- preserves the historical database while avoiding expensive startup counting behavior

Interpretation:

- performance / operability fix
- not an entropy-model change

## Bitcoin tooling

### `src/bip39_btc_generador_direcciones_desde_archivo_v3_0.py`

Role:

- forward derivation from known BIP-39 mnemonic data to public Bitcoin Native SegWit addresses
- deterministic validation/export workflow

### `src/buscador_desde_archivo_v2_2.py`

Role:

- finite verification/search over explicitly user-supplied candidate files
- not a general cryptographic inversion mechanism

## Dataset tooling

### `scripts/generate_sha256s.py`

Role:

- generate `SHA256SUMS.txt` for dataset files
- integrity only

### `scripts/build_dataset_package.py`

Role:

- read dataset manifest
- generate `DATASET_CARD.md`
- generate `metadata.json`
- generate schema.org `dataset.jsonld`
- regenerate SHA-256 file list

### `scripts/build_datasets_index.py`

Role:

- discover dataset-level `metadata.json` files
- build `generated_phrases/DATASETS_INDEX.json`

## Test layer

### `tests/test_v27_core.py`

Current deterministic coverage:

- local-position wrap behavior
- invalid absolute-position handling
- block-number behavior
- zero-entropy BIP-39 checksum/index construction

## Documentation layer

Important technical entry points:

```text
README.md
ARCHITECTURE.md
docs/TECHNICAL_ARCHITECTURE.md
docs/DATA_FLOW.md
docs/API_REFERENCE.md
docs/SQLITE_MODEL.md
docs/BIP39_PIPELINE.md
docs/PRIME_COORDINATE_MODEL.md
docs/SECURITY_MODEL.md
docs/REPRODUCIBILITY.md
docs/VERSION_MATRIX.md
```

## Reading order for source analysis

Recommended order for a new reviewer or AI system:

1. `README.md`
2. `ARCHITECTURE.md`
3. `docs/TECHNICAL_ARCHITECTURE.md`
4. `docs/BIP39_PIPELINE.md`
5. `docs/PRIME_COORDINATE_MODEL.md`
6. `docs/SQLITE_MODEL.md`
7. `tests/`
8. exact `src/` file being analyzed
9. dataset metadata
10. raw generated data
