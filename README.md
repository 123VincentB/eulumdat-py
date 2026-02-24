# pyldt

A Python library for reading and writing **EULUMDAT** (`.ldt`) photometric files — the standard format for luminaire intensity distribution data used in lighting design and photometric testing.

Developed in an ISO 17025 accredited photometry laboratory.

---

## Features

- Parse any valid EULUMDAT file into a clean Python object model
- Full symmetry expansion (ISYM 0–4) into a complete `[mc × ng]` intensity matrix
- Edit header fields (luminaire name, lamp data, photometric factors, geometry, …)
- Save back to a valid EULUMDAT file with correct ISO-8859-1 encoding
- Optional symmetry compression on write
- Safe file naming: auto-increments filename (`_1`, `_2`, …) if destination exists
- No dependencies beyond the Python standard library

---

## Installation

```bash
pip install pyldt
```

> Not yet published on PyPI. Clone the repository and install locally:
>
> ```bash
> git clone https://github.com/123VincentB/pyldt.git
> cd pyldt
> pip install -e .
> ```

---

## Quick start

```python
from pyldt import LdtReader, LdtWriter

# Read
ldt = LdtReader.read("luminaire.ldt")
print(ldt.header.luminaire_name)
print(f"I(C=0°, γ=0°) = {ldt.intensities[0][0]:.1f} cd/klm")

# Edit a header field
ldt.header.date_user = "2026-01-01 / modified"

# Save (adds _1 suffix if file already exists)
saved = LdtWriter.write(ldt, "luminaire_modified.ldt")
print(f"Saved to: {saved}")
```

---

## Examples

| File | Description |
|------|-------------|
| [`examples/01_basic_usage.md`](examples/01_basic_usage.md) | Accessing header fields, lamp data and intensity values |
| [`examples/01_basic_usage.py`](examples/01_basic_usage.py) | Runnable script for the above |
| [`examples/02_polar_diagram.md`](examples/02_polar_diagram.md) | Plotting the polar intensity diagram (4 C-planes) |
| [`examples/02_polar_diagram.py`](examples/02_polar_diagram.py) | Runnable script for the above (requires matplotlib) |

Run any example from the repository root:

```bash
python examples/01_basic_usage.py
python examples/02_polar_diagram.py
```

---

## Project structure

```
pyldt/
├── pyldt/
│   ├── __init__.py      ← Public API
│   ├── model.py         ← LdtHeader, Ldt dataclasses
│   ├── parser.py        ← LdtReader
│   └── writer.py        ← LdtWriter
├── examples/
│   ├── 01_basic_usage.md
│   ├── 01_basic_usage.py
│   ├── 02_polar_diagram.md
│   └── 02_polar_diagram.py
├── tests/
│   ├── test_parser.py
│   └── samples/         ← .ldt test files (10 real manufacturer files)
├── docs/
│   └── eulumdat_format.md
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## EULUMDAT format

EULUMDAT is the standard file format for luminaire photometric data, defined by the LiTG (Deutsche Lichttechnische Gesellschaft, 1990). It is widely used in Europe alongside IES files (North America).

Key concepts:

- **C-planes**: vertical planes through the luminaire vertical axis (azimuth, 0–360°)
- **γ-angles**: elevation angles within each C-plane (0° = nadir, 90° = horizontal, 180° = zenith)
- **ISYM**: symmetry code that allows the file to store only a subset of C-planes
- **Intensities**: tabulated in cd/klm (candela per kilolumen of lamp flux)

See [`docs/eulumdat_format.md`](docs/eulumdat_format.md) for a detailed field-by-field description.

---

## Symmetry types (ISYM)

| ISYM | Description | C-planes stored |
|------|-------------|-----------------|
| 0 | No symmetry | All mc planes |
| 1 | Full rotational symmetry | 1 plane |
| 2 | Symmetry about C0–C180 | mc/2 + 1 planes |
| 3 | Symmetry about C90–C270 | mc/2 + 1 planes |
| 4 | Quadrant symmetry | mc/4 + 1 planes |

`LdtReader.read()` always returns a fully expanded matrix regardless of ISYM.

---

## License

MIT — see [LICENSE](LICENSE).

---

## Context

This library was developed as a practical tool in the context of ISO 17025 accredited photometric testing. It is shared as open-source in the hope that it will be useful to others working with EULUMDAT files in Python.
