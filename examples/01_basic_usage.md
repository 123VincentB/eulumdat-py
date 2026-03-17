# eulumdat-py — Basic usage

This example shows how to read an EULUMDAT file and access the most common fields.

## Reading a file

```python
from pyldt import LdtReader

ldt = LdtReader.read("luminaire.ldt")
h = ldt.header
```

`LdtReader.read()` returns an `Ldt` object with two attributes:

- `ldt.header` — an `LdtHeader` dataclass containing all metadata
- `ldt.intensities` — a 2-D list `[mc × ng]` of intensity values in cd/klm,
  always expanded to the full angular range regardless of the file's ISYM symmetry

---

## Accessing header fields

### Manufacturer and luminaire identification

```python
print(h.company)          # e.g. "ERCO GmbH"
print(h.luminaire_name)   # e.g. "Jilly 65 LED"
```

### Symmetry and angular grid

```python
print(h.isym)   # 0=none, 1=full, 2=C0-C180, 3=C90-C270, 4=quadrant
print(h.mc)     # number of C-planes
print(h.dc)     # angular step between C-planes (degrees)
print(h.ng)     # number of γ-angles per C-plane
print(h.dg)     # angular step between γ-angles (degrees)
```

### Luminaire geometry (mm)

```python
print(h.length)   # overall length
print(h.width)    # overall width
print(h.height)   # overall height
```

### Lamp data — first lamp set

The file may contain one or more lamp sets (`h.n_sets`).
Each lamp property is stored as a list indexed by set number (0-based).

```python
print(h.lamp_flux[0])   # rated luminous flux of the lamp (lm)
print(h.lamp_watt[0])   # rated power (W)
print(h.num_lamps[0])   # number of lamps in the set
print(h.lamp_types[0])  # lamp type string, e.g. "LED"
print(h.lamp_cct[0])    # correlated colour temperature, e.g. "4000K"
print(h.lamp_cri[0])    # colour rendering index, e.g. "80"
```

---

## Accessing intensity values

`ldt.intensities` is a list of lists with shape `[mc][ng]`.
The first index selects the C-plane, the second selects the γ-angle.

```python
# First few values of the first C-plane (C = 0°)
print(ldt.intensities[0][:5])

# Intensity at C = 0°, γ = 0° (nadir)
print(ldt.intensities[0][0])

# Intensity at C = 0°, last γ-angle (usually γ = 90° or 180°)
print(ldt.intensities[0][-1])
```

The C-plane and γ-angle values corresponding to each index are stored in
`h.c_angles` and `h.g_angles`:

```python
print(h.c_angles)   # e.g. [0.0, 2.5, 5.0, ..., 357.5]
print(h.g_angles)   # e.g. [0.0, 5.0, 10.0, ..., 90.0]
```

To look up the index of a specific angle:

```python
c0_idx = h.c_angles.index(0.0)
g45_idx = h.g_angles.index(45.0)
print(ldt.intensities[c0_idx][g45_idx])   # cd/klm at C=0°, γ=45°
```

---

## Converting to absolute candela

Intensity values in the file are normalised to cd/klm.
To convert to absolute candela, multiply by the lamp flux:

```python
flux_klm = h.lamp_flux[0] / 1000.0   # lm → klm

i_abs = [
    [v * flux_klm for v in row]
    for row in ldt.intensities
]

print(i_abs[0][0])   # cd at C=0°, γ=0°
```
