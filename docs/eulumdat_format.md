# EULUMDAT File Format

EULUMDAT is the standard file format for photometric data of luminaires,
defined by the **LiTG** (Deutsche Lichttechnische Gesellschaft) in 1990.
It is a plain-text, line-based format encoded in **ISO-8859-1**.

---

## File structure

The file consists of a fixed-structure header followed by the angular grid
and the intensity table.

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
| 26a–26f | Lamp set 1 | — | 6 lines: NUM_LAMPS, LAMP_TYPE, LAMP_FLUX, CCT, CRI, LAMP_WATT |
| … | Lamp set 2 | — | Same 6 lines repeated for set 2 |
| … | Lamp set N | — | Same 6 lines repeated for set N |
| 27–36 | `DR[1..10]` | float | Direct ratios for 10 zones (%) |
| 37–… | C-angles | float | C-plane angles (°) |
| …–… | γ-angles | float | γ-angles (°) |
| …–end | Intensities | float | cd/klm, one value per line, C-plane by C-plane |

### Lamp sets example

For `N_SETS = 2`, the lamp data occupies **12 consecutive lines** — 6 lines per set:

```
2                        ← N_SETS
1                        ← NUM_LAMPS  set 1
LED-Module               ← LAMP_TYPE  set 1
3500                     ← LAMP_FLUX  set 1 (lm)
3000                     ← CCT        set 1 (K)
80                       ← CRI        set 1
18.5                     ← LAMP_WATT  set 1 (W)
1                        ← NUM_LAMPS  set 2
LED-Module               ← LAMP_TYPE  set 2
3500                     ← LAMP_FLUX  set 2 (lm)
4000                     ← CCT        set 2 (K)
80                       ← CRI        set 2
18.5                     ← LAMP_WATT  set 2 (W)
```

---

## Symmetry (ISYM)

The ISYM field determines how many C-planes are stored in the file.
`LdtReader` always expands the matrix to the full `[Mc × Ng]` size.

| ISYM | Meaning | Planes stored |
|------|---------|---------------|
| 0 | No symmetry | All Mc planes |
| 1 | Full rotational symmetry | 1 plane (C=0°) |
| 2 | Symmetry about C0–C180 plane | Mc/2 + 1 planes |
| 3 | Symmetry about C90–C270 plane | Mc/2 + 1 planes (stored C270→C90) |
| 4 | Double symmetry (quadrant) | Mc/4 + 1 planes |

---

## Intensity values

Intensities are tabulated in **cd/klm** (candela per kilolumen of total lamp
flux). To convert to absolute candela, multiply by the total lamp flux in
kilolumens:

```
I_abs(C, γ) [cd] = I_rel(C, γ) [cd/klm] × Φ_lamp [klm]
```

Values are written one per line, sweeping all γ-angles for each C-plane in
sequence.

---

## Encoding

EULUMDAT files use **ISO-8859-1** (Latin-1) encoding. `pyldt` reads files
with `errors="ignore"` for robustness and writes in ISO-8859-1.

---

## References

- LiTG, *EULUMDAT — Format Description*, Deutsche Lichttechnische Gesellschaft, 1990.
- Erco Leuchten GmbH, *EULUMDAT File Format* (widely cited technical summary).
