# `Generador_V2_4_MultiGrupos.py` — sequential multi-group generation

## Motivation
Earlier versions generated one candidate at a time. V2.4 adds batch export of multiple 12-word groups while retaining the infinite absolute-coordinate sequence and structural filter.

## Sequential rule
For a selected first absolute position, the first group is generated normally. The next group's starting absolute position is set to one position after the previous group's final absolute position. This creates a continuous sequence of groups rather than N independent restarts.

## Batch output
The user chooses how many groups to generate and a destination text file. The program accumulates generated candidate metadata and writes the mnemonic phrases sequentially.

## Prime-calculation change
V2.4 collects the requested absolute positions from all generated groups and resolves the needed odd primes in a consolidated sieve pass. This reduces repeated setup relative to calculating each group's absolute primes independently.

## Inherited mechanisms
- 128-bit entropy field + 4-bit checksum;
- fixed first local index + 117-bit `secrets` tail;
- infinite local/absolute lift;
- structural rejection;
- local SQLite SHA-256 duplicate history.

## Performance limitation
Although batch prime calculation improves reuse, resolving every absolute prime for large multi-group exports can dominate runtime. This limitation motivated the later V2.5 Turbo design, which calculates only the last 12 absolute primes when only the last series needs to be shown in the GUI.
