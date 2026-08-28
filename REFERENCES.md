# References

## Bitcoin standards

- **BIP-39 — Mnemonic code for generating deterministic keys**  
  https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki  
  Defines ENT/CS/MS, 11-bit word indexing, checksum generation, mnemonic-to-seed PBKDF2-HMAC-SHA512, and the optional passphrase.
- **BIP-32 — Hierarchical Deterministic Wallets**  
  https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
- **BIP-84 — Derivation scheme for P2WPKH based accounts**  
  https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki  
  Defines the `84'` purpose and the account path structure used by the Native SegWit utilities in this repository.

## Python randomness

- **Python `secrets` module**  
  https://docs.python.org/3/library/secrets.html  
  The generators use `secrets.randbits(...)` for operating-system-backed cryptographically strong randomness.

## Repository / large-data management

- **GitHub Docs — About large files on GitHub**  
  https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- **GitHub Docs — About Git Large File Storage**  
  https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage

## Project-source note

The mathematical claims, experimental results, reference sequences, and software chronology are documented in the project's technical manuscript. Where the manuscript distinguishes *proved*, *reproduced*, *observed*, and *experimental* results, that distinction is preserved in the English translation and repository documentation.
