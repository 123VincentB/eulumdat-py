# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-03-16

### Changed
- Version bump to 1.0.0 — stable release following validation on 42 real manufacturer LDT files

---

## [0.1.4] - 2026-03-13

### Fixed
- `parser.py`: correct C-plane expansion for ISYM=2 (`_expand_to_full_matrix`)
  — mirror of index `i` is `mc-i`, not `half-1+(half-i)` (#1)
- `parser.py`: correct C-plane expansion for ISYM=3 (`_expand_to_full_matrix`)
  — mirror of C is `(180°-C) mod 360°`, not `(C+180°) mod 360°` (#1)

---

## [0.1.3] - 2026-02-25

### Added
- Examples: `01_basic_usage.md` and `01_basic_usage.py`
- Examples: `02_polar_diagram.md` and `02_polar_diagram.py` — polar intensity diagram (4 C-planes)

### Changed
- `pyproject.toml`: enriched keywords and classifiers for better PyPI discoverability
- `pyproject.toml`: added `Documentation` and `Bug Tracker` URLs
- `README.md`: added PyPI version, Python version and licence badges

---

## [0.1.2] - 2026-02-24

### Fixed
- `pyproject.toml`: corrected `build-backend` (`setuptools.build_meta`)
- `pyproject.toml`: added `wheel` to build requirements
- `.gitignore`: fixed PNG exception rule order

---

## [0.1.1] - 2026-02-20

### Fixed
- `parser.py`: BOM UTF-8 stripped before latin-1 decoding (ERCO files)
- `parser.py`: introduced `pop_raw()` to preserve empty text fields (e.g. empty `lumcat`)
- `parser.py`: corrected `_mc_range_from_isym` for ISYM=3

### Added
- `tests/test_parser.py`: 23 test functions (~80 cases) covering 10 real manufacturer files
- `tests/samples/`: 10 real EULUMDAT files (Tulux, Regent, Zumtobel, ERCO, TRILUX, LEDiL, Signify, Waldmann)
- `docs/eulumdat_format.md`: encoding section updated, real-world parser notes added

---

## [0.1.0] - 2026-02-19

### Added
- Initial release
- `LdtReader.read()`: parse EULUMDAT files with full symmetry expansion (ISYM 0–4)
- `LdtWriter.write()`: save EULUMDAT files with optional symmetry compression
- `LdtHeader` dataclass covering all standard EULUMDAT header fields
- `Ldt` dataclass holding header and full intensity matrix
- Safe file naming (auto-increment suffix if destination exists)
- ISO-8859-1 encoding on write (EULUMDAT standard)
- `docs/eulumdat_format.md`: complete technical reference for the EULUMDAT format
- `examples/basic_usage.py`: initial usage example
