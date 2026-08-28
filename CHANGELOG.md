# Version History and Development Trace

This history is reconstructed only from the supplied source files, the technical manuscript, and source snapshots produced during the documented development. **No release date is assigned where the source does not provide one.**

## Data foundation

### Base spreadsheet — odd-prime positions
- Established positions `1..2048` and the first 2,048 odd primes.
- Position 1 corresponds to prime 3.

### Base spreadsheet + BIP-39 English words
- Added the 2,048 English words in index order.
- Produced the deterministic `position ↔ odd prime ↔ word` map serialized as `datos_2048.json`.
- This mapping is representational; it does not add entropy.

## 12-word generator line

### V1 — finite generator (`generador_12_palabras.py`)
- Finite initial-position domain: `1..2048`.
- 12-word / 132-bit encoding: 128-bit entropy field + 4-bit SHA-256 checksum.
- Initial word index fixes the first 11 entropy bits.
- Remaining 117 bits generated with `secrets.randbits(117)`.
- Local SHA-256 phrase history in SQLite prevents local re-emission without storing the phrase in clear text.
- Tkinter interface displays position, prime, and word layers.

### V2 — infinite absolute coordinate
- Split each symbol into a local index `1..2048` and an absolute positive position.
- The next local symbol is lifted to the first strictly later absolute position with the same residue modulo 2048.
- Absolute positions and corresponding odd primes therefore remain strictly increasing even when local indices decrease.
- Added segmented odd-prime lookup for requested absolute positions.
- No extra cryptographic entropy is created by the absolute coordinate.

### V2.2 — consecutive-pattern rejection
- Added rejection of local ±1 consecutive sequences, including wrap-around at `2048 ↔ 1`.
- The manuscript records 4,096 raw directional patterns and 249 that also satisfy the 4-bit checksum.

### V2.3 — total linear filter
- Expanded rejection to strict ascending/descending local order with arbitrary gaps within one traversal of the 2,048-position cycle.
- Added fixed-step modular progression rejection, including step zero.
- The filter is an acceptance policy, not an entropy test.

### V3 finite — strengthened total filter (`generador_v3_finita_filtro_total_reforzado.py`)
- Preserved the finite `1..2048` domain.
- Strengthened structural rejection with fixed-step progressions, strict ascending/descending order, unordered 12-position consecutive sets, and an explicit cyclic ordered-consecutive check.

### V3 infinite — strengthened total filter (`generador_v3_infinita_filtro_total_reforzado.py`)
- Preserved the infinite local/absolute lift architecture.
- Added explicit detection of 12-position consecutive local ranges, including wrap-around, on top of fixed-step and strict-order filters.
- Retained segmented absolute-prime lookup.

## 24-word branch

### Infinite 24-word generator (`generador_24_palabras_infinita_filtro_lineal_total.py`)
- Switched to the BIP-39 24-word bit structure: 256 entropy bits + 8 checksum bits = 264 bits = 24 × 11.
- Initial local position fixes 11 bits; the implementation generates the remaining 245 bits with `secrets`.
- Retained the infinite absolute-coordinate representation, structural rejection, local SQLite duplicate hashes, and segmented prime lookup.

## Multi-group and performance line

### V2.4 MultiGroups (`Generador_V2_4_MultiGrupos.py`)
- Added iterative generation of N sequential 12-word groups.
- Each group starts after the last absolute position of the previous group.
- Writes multiple phrases to one text file.
- Aggregates absolute-prime requests for the generated groups into a single prime-sieve pass.

### V2.5 Turbo — intermediate development milestone
- Reused one SQLite connection/transaction instead of per-phrase setup.
- Added batched SQLite commits and buffered file writes.
- Added multi-process segmented prime sieving; default worker target approximately 75% of logical CPUs.
- Avoided calculating absolute primes for every exported phrase when only the final displayed series needed those values; computes only the final 12 absolute primes for the GUI.

### V2.6 automatic range — intermediate development milestone
- Added start value, inclusive end value, groups per value, and groups per output file.
- Automatic file naming and session directory creation.
- Automatically increments the start value by one after the requested group count is completed.
- Added run manifest and safe stop behavior.

### V2.7 AUTO Turbo + Timers (`Generador_V2_7_AUTO_Turbo_Cronometros.py`)
- Removed per-phrase Tkinter progress events.
- GUI receives events only when a file starts/completes and when a value completes.
- Added low-cost runtime heartbeat and a generation timer so long file batches do not appear frozen.
- Retained SQLite SHA-256 duplicate prevention.
- Retained final computation of the last 12 absolute primes.
- Added a separate timer for that final prime-sieve phase.

## Bitcoin utility line

### File-based finder V2.2 (`buscador_desde_archivo_v2_2.py`)
- Added BIP-39 validation and pure-Python Bitcoin Native SegWit derivation.
- Default path: `m/84'/0'/0'/0/0`.
- Reads finite candidates from TXT/CSV/TSV/XLSX.
- Address lookup tests only candidates explicitly loaded from the selected file; it does not mathematically invert an address.
- This repository documents it as an authorized finite-candidate verification tool, not as a general wallet-recovery mechanism.

### Address exporter V3.0 (`bip39_btc_generador_direcciones_desde_archivo_v3_0.py`)
- Reoriented the V2.2 derivation engine into a forward batch operation: mnemonic → Native SegWit address.
- Preserves input order.
- Does not deduplicate the ordered export, so line-to-line correspondence is retained.
- Writes one address per detected phrase; derivation/validation failures are represented on that same output position with an `ERROR_BIP39:` marker.

## Documentation milestone

### Technical manuscript — 24 August 2026
- Consolidated the prime-coordinate model, twin-prime specialization, modular compression, 2,048-position map, 12-word entropy structure, generator versions, limitations, and future work.
- Explicitly states that prime labels and the infinite coordinate add no cryptographic entropy and that the software is experimental and unaudited.
