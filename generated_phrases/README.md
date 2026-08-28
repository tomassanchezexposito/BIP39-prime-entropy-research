# Generated Phrase Corpus

**PUBLIC TEST DATA ONLY. NEVER PUT A FUNDED OR POTENTIALLY FUNDED WALLET MNEMONIC HERE.**

This directory is intentionally shipped without mnemonic corpora. Add only sequences that are explicitly designated as public, never-funded test vectors.

After adding/removing corpus files, run from the repository root:

```bash
python scripts/update_generated_phrases_index.py
```

The script refreshes:

- `generated_phrases/MANIFEST.tsv` — one row per corpus file with line count, byte size, SHA-256, and mtime;
- `generated_phrases/DATASET_STATUS.json` — machine-readable totals and `updated_at_utc`;
- `generated_phrases/STATUS.md` — human-readable update indicator.

## Large files

GitHub ordinary Git storage is not a good fit for very large generated corpora. `.gitattributes` is prepared to use Git LFS for `generated_phrases/**/*.txt`. Review GitHub's current large-file/LFS limits before pushing large runs.
