# `Generador_V2_7_AUTO_Turbo_Cronometros.py` — automatic ranged generation with timers

## Development goal
Large automatic runs exposed a UI bottleneck: per-phrase Tkinter updates could accumulate far faster than the GUI could render them. V2.7 separates the generation engine from high-frequency GUI reporting while retaining the SQLite duplicate history and final absolute-prime calculation.

## Automatic generation plan
The operator configures:

- initial value;
- inclusive final value;
- total groups per value;
- maximum groups per output file;
- output prefix and destination directory;
- CPU process count for the prime-sieve stage.

For each value, the engine generates the requested sequential groups and splits them into automatically named files. After that value is complete, the next run starts at `value + 1`, continuing until the inclusive final value.

## File-level GUI events
The V2.7 engine does not send a GUI event for every phrase. It reports only file start, file completion, and value completion. A low-cost shared `runtime_state` is updated at existing internal checkpoints, allowing Tkinter to display a heartbeat without queuing millions of progress callbacks.

## Timers
Two timings are explicitly separated:

1. **generation timer** — covers phrase generation, duplicate checking, and file creation;
2. **absolute-prime timer** — starts only after all phrase files are created and measures the final computation of the last 12 absolute primes.

The final message reports generation time, final-prime calculation time, and total time.

## Duplicate control
The generator continues to compute SHA-256 of each phrase and uses SQLite `INSERT OR IGNORE` semantics so a locally recorded phrase is rejected and regenerated.

## Prime performance
The segmented sieve can use multiple processes. The source selects approximately 75% of logical CPUs by default and retains a serial path for smaller target ordinals where process startup would be wasteful.

## Output traceability
A session directory and `MANIFIESTO.tsv` document which files were created, the associated starting value/part, generated counts, and absolute-position continuation metadata.
