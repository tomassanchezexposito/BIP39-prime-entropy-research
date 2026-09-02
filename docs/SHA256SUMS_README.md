# SHA256SUMS

## Purpose

`SHA256SUMS.txt` records SHA-256 digests for dataset files so users and automated systems can verify byte-for-byte integrity.

A matching hash does not prove generator security, BIP-39 correctness, global uniqueness, or extra entropy.

## Generate hashes

Use:

```bash
python scripts/generate_sha256s.py generated_phrases/<dataset-directory>
```

The script creates or replaces `SHA256SUMS.txt`.

## Verify one file on Windows PowerShell

```powershell
Get-FileHash -Algorithm SHA256 .\path\to\file.txt
```

Compare the result with `SHA256SUMS.txt`.
