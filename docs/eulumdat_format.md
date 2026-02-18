# EULUMDAT File Format

EULUMDAT is the standard file format for photometric data of luminaires,
defined by the **LiTG** (Deutsche Lichttechnische Gesellschaft) in 1990.
It is a plain-text, line-based format encoded in **ISO-8859-1**.

---

## File structure

The file consists of a fixed-structure header followed by the angular grid
and the intensity table.

> **Note on line numbering:** Lines 1–26 are fixed. From line 27 onward, line
> numbers shift depending on `N_SETS` (number of lamp sets). Each lamp set
> occupies exactly 6 consecutive lines. With N sets, lamp data spans lines
> 27 to 26+6N. All subsequent sections (direct ratios, angles, intensities)
> start at line 27+6N.

| Line(s) | Field | Type | Description |
|---------|-------|------|-------------|
| 1 | `COMPANY` | str | Manufacturer name |
| 2 | `ITYP` | int | Luminaire type (0=point, 1=linear, 2=area) |
| 3 | `ISYM` | int | Symmetry indicator (see below) |
| 4 | `Mc` | int | Number of C-planes |
| 5 | `Dc` | float | Angular step between C-planes (°) |
| 6 | `Ng` | int | Number of γ-angles per C-plane |
| 7 | `Dg` | float | Angular step between γ-angles (°) |
| 8 | `REPORT_NO` | str | Measurement report number |
| 9 | `LUMINAIRE_NAME` | str | Luminaire name |
| 10 | `LUMINAIRE_NO` | str | Luminaire catalog number |
| 11 | `FILE_NAME` | str | File name |
| 12 | `DATE_USER` | str | Date and user |
| 13 | `LENGTH` | float | Luminaire length (mm) |
| 14 | `WIDTH` | float | Luminaire width (mm) |
| 15 | `HEIGHT` | float | Luminaire height (mm) |
| 16 | `LENGTH_LUM` | float | Luminous area length (mm) |
| 17 | `WIDTH_LUM` | float | Luminous area width (mm) |
| 18 | `H_C0` | float | Height of luminous area at C=0° (mm) |
| 19 | `H_C90` | float | Height of luminous area at C=90° (mm) |
| 20 | `H_C180` | float | Height of luminous area at C=180° (mm) |
| 21 | `H_C270` | float | Height of luminous area at C=270° (mm) |
| 22 | `DFF` | float | Downward flux fraction (%) |
| 23 | `LORL` | float | Light output ratio luminaire (%) |
| 24 | `CONV_FACTOR` | float | Conversion factor |
| 25 | `TILT` | float | Luminaire tilt during measurement (°) |
| 26 | `N_SETS` | int | Number of lamp sets |
| 27 | `NUM_LAMPS` | int | Number of lamps — set 1 |
| 28 | `LAMP_TYPE` | str | Lamp type description — set 1 |
| 29 | `LAMP_FLUX` | float | Total luminous flux (lm) — set 1 |
| 30 | `CCT` | str | Colour temperature (K) — set 1 |
| 31 | `CRI` | str | Colour rendering index — set 1 |
| 32 | `LAMP_WATT` | float | Power (W) — set 1 |
| … | *(repeat 6 lines for each additional set)* | | |
| 27+6N | `DR[1]`–`DR[10]` | float | Direct ratios for 10 zones (%), one value per line |
| 37+6N | C-angles | float | C-plane angles (°), one value per line (Mc values) |
| 37+6N+Mc | γ-angles | float | γ-angles (°), one value per line (Ng values) |
| 37+6N+Mc+Ng | Intensities | float | cd/klm, one value per line, C-plane by C-plane |

> N = N_SETS. Line numbers from line 27 onward shift by 6 for each additional lamp set.

---

### Lamp sets example

The lamp data section is the only variable-length section of the header.
Each set always occupies exactly 6 lines.

**N_SETS = 1** (most common case — 32 lines of header before direct ratios):

```
...
26: 1            ← N_SETS
27: 1            ← NUM_LAMPS
28: LED-Module   ← LAMP_TYPE
29: 3500         ← LAMP_FLUX (lm)
30: 3000         ← CCT (K)
31: 80           ← CRI
32: 18.5         ← LAMP_WATT (W)
33: 0.0          ← DR[1]  (direct ratios start here)
...
42: 0.0          ← DR[10]
43: 0            ← C-angles start here
...
```

**N_SETS = 2** (lamp data spans lines 27–38, direct ratios start at line 39):

```
...
26: 2            ← N_SETS
27: 1            ← NUM_LAMPS  set 1
28: LED-Module   ← LAMP_TYPE  set 1
29: 3500         ← LAMP_FLUX  set 1 (lm)
30: 3000         ← CCT        set 1 (K)
31: 80           ← CRI        set 1
32: 18.5         ← LAMP_WATT  set 1 (W)
33: 1            ← NUM_LAMPS  set 2
34: LED-Module   ← LAMP_TYPE  set 2
35: 3500         ← LAMP_FLUX  set 2 (lm)
36: 4000         ← CCT        set 2 (K)
37: 80           ← CRI        set 2
38: 18.5         ← LAMP_WATT  set 2 (W)
39: 0.0          ← DR[1]  (direct ratios start here)
...
48: 0.0          ← DR[10]
49: 0            ← C-angles start here
...
```

---

## Symmetry (ISYM)

The ISYM field declares the symmetry of the luminaire's intensity distribution.

When ISYM ≠ 0, the intensity values stored in the file are **already symmetrised**
before writing: for each pair of mirror planes, the values are averaged. This serves
two purposes: reducing file size (fewer C-planes to store) and smoothing the measured
distribution to eliminate measurement artefacts.

`LdtReader` always expands the matrix to the full `[Mc × Ng]` size on read.

| ISYM | Symmetry | Symmetrisation rule (applied before writing) | C-planes written to file |
|------|----------|----------------------------------------------|--------------------------|
| 0 | None | No averaging — raw measured values | C=0° to C=360°−Dc (all Mc planes) |
| 1 | Full rotational | I_sym(γ) = average of I(C, γ) over all C-planes | C=0° only (1 plane) |
| 2 | About C0–C180 | I_sym(C, γ) = [ I(C, γ) + I(360°−C, γ) ] / 2 | C=0° to C=180° (inclusive) |
| 3 | About C90–C270 | I_sym(C, γ) = [ I(C, γ) + I(180°−C, γ) ] / 2 | C=270° down to C=90° *(decreasing order)* |
| 4 | Quadrant (C0–C180 and C90–C270) | I_sym(C, γ) = average of { I(C,γ), I(360°−C,γ), I(180°−C,γ), I(180°+C,γ) } | C=0° to C=90° (inclusive) |

> **ISYM=0:** Raw measured values, no averaging. This is the only mode where the full
> asymmetry of the luminaire is preserved.

> **ISYM=3 storage order:** C-planes are written in *decreasing* order from C=270° down
> to C=90°. This specific ordering is required for correct import in DIALux and Relux —
> using increasing order causes the intensity distribution to appear mirrored.

---

## Intensity values

Intensities are tabulated in **cd/klm** (candela per kilolumen of total lamp flux).
To convert to absolute candela, use either of the two equivalent forms:

```
I_abs(C, γ) [cd] = I_rel(C, γ) [cd/klm] × Φ_lamp [lm] / 1000
I_abs(C, γ) [cd] = I_rel(C, γ) [cd/klm] × Φ_lamp [klm]
```

> The first form is more practical since lamp flux (Φ_lamp) is typically expressed
> in lm, not klm.

Values are written one per line, sweeping all γ-angles for each C-plane in sequence.

---

## Encoding

EULUMDAT files use **ISO-8859-1** (Latin-1) encoding. `pyldt` reads files
with `errors="ignore"` for robustness and writes in ISO-8859-1.

---

## References

- LiTG, *EULUMDAT — Format Description*, Deutsche Lichttechnische Gesellschaft, 1990.
- Erco Leuchten GmbH, *EULUMDAT File Format* (widely cited technical summary).
