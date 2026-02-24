"""
Basic usage example for pyldt.

Demonstrates how to read an EULUMDAT file and access the most common fields.
Run from the root of the pyldt/ repository:

    python examples/01_basic_usage.py
"""

from pyldt import LdtReader

# ── Load file ─────────────────────────────────────────────────────────────────
ldt = LdtReader.read("tests/samples/sample2.ldt")
h = ldt.header

# ── Identification ────────────────────────────────────────────────────────────
print("=== Identification ===")
print(f"  Company        : {h.company}")
print(f"  Luminaire name : {h.luminaire_name}")
print(f"  Luminaire no.  : {h.luminaire_number}")
print(f"  Report no.     : {h.report_number}")
print(f"  Date / User    : {h.date_user}")

# ── Symmetry and angular grid ─────────────────────────────────────────────────
print("\n=== Angular grid ===")
print(f"  ISYM : {h.isym}  (0=none, 1=full, 2=C0-C180, 3=C90-C270, 4=quadrant)")
print(f"  MC   : {h.mc} C-planes,  step {h.dc}°")
print(f"  NG   : {h.ng} γ-angles,  step {h.dg}°")

# ── Geometry ──────────────────────────────────────────────────────────────────
print("\n=== Geometry (mm) ===")
print(f"  Length : {h.length}")
print(f"  Width  : {h.width}")
print(f"  Height : {h.height}")

# ── Lamp sets ─────────────────────────────────────────────────────────────────
print(f"\n=== Lamp sets ({h.n_sets} set(s)) ===")
for k in range(h.n_sets):
    print(f"  Set {k+1}:")
    print(f"    num_lamps  : {h.num_lamps[k]}")
    print(f"    lamp_type  : {h.lamp_types[k]}")
    print(f"    lamp_flux  : {h.lamp_flux[k]} lm")
    print(f"    lamp_watt  : {h.lamp_watt[k]} W")
    print(f"    CCT        : {h.lamp_cct[k]}")
    print(f"    CRI        : {h.lamp_cri[k]}")

# ── Intensity matrix ──────────────────────────────────────────────────────────
print("\n=== Intensity matrix ===")
print(f"  Shape : {len(ldt.intensities)} C-planes × {len(ldt.intensities[0])} γ-angles")
print(f"  First values of C=0° plane : {[round(v, 2) for v in ldt.intensities[0][:5]]} ...")

# Look up a specific angle using c_angles / g_angles
c0_idx  = h.c_angles.index(0.0)
g0_idx  = h.g_angles.index(0.0)
g45_idx = min(range(len(h.g_angles)), key=lambda i: abs(h.g_angles[i] - 45.0))

print(f"\n  I(C=0°, γ= 0°) = {ldt.intensities[c0_idx][g0_idx]:.2f} cd/klm")
print(f"  I(C=0°, γ=45°) = {ldt.intensities[c0_idx][g45_idx]:.2f} cd/klm")

# ── Convert to absolute candela ───────────────────────────────────────────────
print("\n=== Absolute candela (first lamp set) ===")
flux_klm = h.lamp_flux[0] / 1000.0
i_abs_nadir = ldt.intensities[c0_idx][g0_idx] * flux_klm
print(f"  Lamp flux      : {h.lamp_flux[0]} lm = {flux_klm:.3f} klm")
print(f"  I(C=0°, γ=0°)  = {ldt.intensities[c0_idx][g0_idx]:.2f} cd/klm × {flux_klm:.3f} klm"
      f" = {i_abs_nadir:.1f} cd")
