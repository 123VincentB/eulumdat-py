# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.2] - 2026-02-24

### Added
- `LdtReader.read()`: parse EULUMDAT files with full symmetry expansion (ISYM 0–4)
- `LdtWriter.write()`: save EULUMDAT files with optional symmetry compression
- `LdtHeader` dataclass covering all standard EULUMDAT header fields
- `Ldt` dataclass holding header and full intensity matrix
- Safe file naming (auto-increment suffix if destination exists)
- ISO-8859-1 encoding on write (EULUMDAT standard)
