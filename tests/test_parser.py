"""
Tests for pyldt LdtReader and LdtWriter.

Run with:
    pytest tests/ -v

Sample files expected in tests/samples/:
    sample1.ldt  — Tulux,   Isym=4, Mc=144, Ng=73,  N_sets=2
    sample2.ldt  — Regent,  Isym=2, Mc=72,  Ng=37,  N_sets=1
    sample3.ldt  — Regent,  Isym=0, Mc=24,  Ng=37,  N_sets=1
    sample4.ldt  — Zumtobel,Isym=4, Mc=24,  Ng=37,  N_sets=1
    sample5.ldt  — ERCO,    Isym=1, Mc=1,   Ng=91,  N_sets=1  (UTF-8 BOM)
    sample6.ldt  — TRILUX,  Isym=3, Mc=144, Ng=73,  N_sets=1  (empty lumcat)
"""

import tempfile
from pathlib import Path

import pytest

from pyldt import LdtReader, LdtWriter

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SAMPLES_DIR = Path(__file__).parent / "samples"


def sample(n: int) -> Path:
    return SAMPLES_DIR / f"sample{n}.ldt"


def n_stored_planes(mc: int, isym: int) -> int:
    """Expected number of C-planes physically stored for a given Isym."""
    if isym == 0: return mc
    if isym == 1: return 1
    if isym == 2: return mc // 2 + 1
    if isym == 3: return mc // 2 + 1
    if isym == 4: return mc // 4 + 1
    raise ValueError(f"Unknown isym={isym}")


# ---------------------------------------------------------------------------
# Smoke tests — all files parse without exception
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_read_no_exception(n):
    """LdtReader.read() must not raise on any sample file."""
    ldt = LdtReader.read(sample(n))
    assert ldt is not None
    assert ldt.header is not None
    assert ldt.intensities is not None


# ---------------------------------------------------------------------------
# Header fields — known values from manufacturer files
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n, expected", [
    (1, {"company": "Tulux",     "isym": 4, "mc": 144, "ng": 73, "n_sets": 2}),
    (2, {"company": "Regent",    "isym": 2, "mc": 72,  "ng": 37, "n_sets": 1}),
    (3, {"company": "Regent",    "isym": 0, "mc": 24,  "ng": 37, "n_sets": 1}),
    (4, {"company": "ZUMTOBEL",  "isym": 4, "mc": 24,  "ng": 37, "n_sets": 1}),
    (5, {"company": "ERCO GmbH", "isym": 1, "mc": 1,   "ng": 91, "n_sets": 1}),
    (6, {"company": "TRILUX",    "isym": 3, "mc": 144, "ng": 73, "n_sets": 1}),
])
def test_header_fields(n, expected):
    h = LdtReader.read(sample(n)).header
    assert h.company   == expected["company"]
    assert h.isym      == expected["isym"]
    assert h.mc        == expected["mc"]
    assert h.ng        == expected["ng"]
    assert h.n_sets    == expected["n_sets"]


# ---------------------------------------------------------------------------
# Lamp sets
# ---------------------------------------------------------------------------

def test_lamp_sets_single():
    """sample2: 1 set, flux=4600 lm, watt=29 W."""
    h = LdtReader.read(sample(2)).header
    assert len(h.lamp_flux) == 1
    assert h.lamp_flux[0] == pytest.approx(4600.0)
    assert h.lamp_watt[0] == pytest.approx(29.0)


def test_lamp_sets_double():
    """sample1: 2 sets with different fluxes."""
    h = LdtReader.read(sample(1)).header
    assert len(h.lamp_flux) == 2
    assert h.lamp_flux[0] == pytest.approx(1983.0)
    assert h.lamp_flux[1] == pytest.approx(2643.0)


def test_lamp_sets_num_lamps_negative():
    """sample5 (ERCO): num_lamps=-1 is a valid value meaning 'not specified'."""
    h = LdtReader.read(sample(5)).header
    assert h.num_lamps[0] == -1


# ---------------------------------------------------------------------------
# Angular grids
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_c_angles_count(n):
    """c_angles must contain exactly Mc values."""
    h = LdtReader.read(sample(n)).header
    assert len(h.c_angles) == h.mc


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_g_angles_count(n):
    """g_angles must contain exactly Ng values."""
    h = LdtReader.read(sample(n)).header
    assert len(h.g_angles) == h.ng


def test_c_angles_start_zero():
    """C-angles must start at 0° for Isym 0, 1, 2, 4."""
    for n in [2, 3, 4, 5]:
        h = LdtReader.read(sample(n)).header
        assert h.c_angles[0] == pytest.approx(0.0), f"sample{n}: c_angles[0] != 0"


def test_g_angles_start_zero():
    """G-angles must start at 0°."""
    for n in range(1, 7):
        h = LdtReader.read(sample(n)).header
        assert h.g_angles[0] == pytest.approx(0.0), f"sample{n}: g_angles[0] != 0"


# ---------------------------------------------------------------------------
# Intensity matrix dimensions
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_intensity_matrix_shape_expanded(n):
    """After expansion, intensities must be [Mc x Ng]."""
    ldt = LdtReader.read(sample(n), expand_symmetry=True)
    h = ldt.header
    assert len(ldt.intensities) == h.mc
    assert all(len(row) == h.ng for row in ldt.intensities)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_intensity_matrix_shape_compressed(n):
    """Without expansion, intensities must be [n_stored x Ng]."""
    ldt = LdtReader.read(sample(n), expand_symmetry=False)
    h = ldt.header
    expected_planes = n_stored_planes(h.mc, h.isym)
    assert len(ldt.intensities) == expected_planes
    assert all(len(row) == h.ng for row in ldt.intensities)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_intensity_values_non_negative(n):
    """All intensity values must be >= 0."""
    ldt = LdtReader.read(sample(n))
    for row in ldt.intensities:
        assert all(v >= 0.0 for v in row)


# ---------------------------------------------------------------------------
# Specific edge cases
# ---------------------------------------------------------------------------

def test_bom_stripped(tmp_path):
    """sample5 (ERCO): UTF-8 BOM must be stripped — company must not start with BOM char."""
    h = LdtReader.read(sample(5)).header
    assert not h.company.startswith("\ufeff")
    assert not h.company.startswith("﻿")
    assert h.company == "ERCO GmbH"


def test_empty_lumcat(tmp_path):
    """sample6 (TRILUX): empty LUMINAIRE_NO must be read without shifting subsequent fields."""
    h = LdtReader.read(sample(6)).header
    assert h.luminaire_number == ""
    # The lamp set must still be correct — would be wrong if the empty line was skipped
    assert h.n_sets == 1
    assert h.lamp_flux[0] == pytest.approx(1800.0)
    assert h.lamp_watt[0] == pytest.approx(17.0)


def test_isym3_stored_planes():
    """sample6 (Isym=3, Mc=144): must store Mc//2+1 = 73 planes."""
    ldt = LdtReader.read(sample(6), expand_symmetry=False)
    h = ldt.header
    assert h.isym == 3
    assert len(ldt.intensities) == h.mc // 2 + 1  # 73


def test_isym4_stored_planes():
    """sample4 (Isym=4, Mc=24): must store Mc//4+1 = 7 planes."""
    ldt = LdtReader.read(sample(4), expand_symmetry=False)
    h = ldt.header
    assert h.isym == 4
    assert len(ldt.intensities) == h.mc // 4 + 1  # 7


def test_isym1_stored_planes():
    """sample5 (Isym=1, Mc=1): must store exactly 1 plane."""
    ldt = LdtReader.read(sample(5), expand_symmetry=False)
    assert len(ldt.intensities) == 1


# ---------------------------------------------------------------------------
# Round-trip tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_roundtrip_header(n, tmp_path):
    """Write then re-read: all header scalar fields must be identical."""
    ldt1 = LdtReader.read(sample(n))
    out = tmp_path / f"sample{n}_rt.ldt"
    LdtWriter.write(ldt1, out, overwrite=True)
    ldt2 = LdtReader.read(out)
    h1, h2 = ldt1.header, ldt2.header

    assert h1.company        == h2.company
    assert h1.isym           == h2.isym
    assert h1.mc             == h2.mc
    assert h1.ng             == h2.ng
    assert h1.dc             == pytest.approx(h2.dc)
    assert h1.dg             == pytest.approx(h2.dg)
    assert h1.n_sets         == h2.n_sets
    assert h1.lamp_flux      == pytest.approx(h2.lamp_flux)
    assert h1.lamp_watt      == pytest.approx(h2.lamp_watt)
    assert h1.luminaire_name == h2.luminaire_name
    assert h1.luminaire_number == h2.luminaire_number


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_roundtrip_intensities(n, tmp_path):
    """Write then re-read: intensity matrix must match within 1e-5 (float formatting loss)."""
    ldt1 = LdtReader.read(sample(n))
    out = tmp_path / f"sample{n}_rt.ldt"
    LdtWriter.write(ldt1, out, overwrite=True)
    ldt2 = LdtReader.read(out)

    assert len(ldt1.intensities) == len(ldt2.intensities)
    for ci, (r1, r2) in enumerate(zip(ldt1.intensities, ldt2.intensities)):
        for gi, (v1, v2) in enumerate(zip(r1, r2)):
            assert abs(v1 - v2) < 1e-5, (
                f"sample{n} C[{ci}] γ[{gi}]: {v1} != {v2} (diff={abs(v1-v2):.2e})"
            )


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6])
def test_roundtrip_matrix_shape(n, tmp_path):
    """Write then re-read: matrix shape must be preserved."""
    ldt1 = LdtReader.read(sample(n))
    out = tmp_path / f"sample{n}_rt.ldt"
    LdtWriter.write(ldt1, out, overwrite=True)
    ldt2 = LdtReader.read(out)
    assert len(ldt1.intensities) == len(ldt2.intensities)
    assert len(ldt1.intensities[0]) == len(ldt2.intensities[0])
