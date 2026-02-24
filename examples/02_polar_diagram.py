"""
Polar intensity diagram for an EULUMDAT file.

Plots the four principal C-planes (C=0°, 90°, 180°, 270°):
  - C=0°  and C=180° : solid lines
  - C=90° and C=270° : dashed lines

Convention:
  - γ=0° (nadir) at the bottom
  - C=0° and C=90° on the right half
  - C=180° and C=270° on the left half
  - Radial axis in cd/klm

Run from the root of the pyldt/ repository:

    python examples/02_polar_diagram.py
"""

import numpy as np
import matplotlib.pyplot as plt
from pyldt import LdtReader

# ── Load file ─────────────────────────────────────────────────────────────────
ldt = LdtReader.read("tests/samples/sample1.ldt")
h = ldt.header

print(f"Company        : {h.company}")
print(f"Luminaire name : {h.luminaire_name}")
print(f"ISYM           : {h.isym}")
print(f"MC / DC        : {h.mc} planes / {h.dc}°")
print(f"NG / DG        : {h.ng} angles / {h.dg}°")

# ── Helper: extract one C-plane by angle ─────────────────────────────────────
def get_plane(target_angle: float) -> np.ndarray:
    """Return the intensity array (cd/klm) for the given C-plane angle (degrees)."""
    match = min(h.c_angles, key=lambda x: abs(x - target_angle))
    if abs(match - target_angle) > 0.1:
        raise ValueError(f"C-plane {target_angle}° not found (closest: {match}°)")
    idx = h.c_angles.index(match)
    return np.array(ldt.intensities[idx])

# ── Angular grid in radians ───────────────────────────────────────────────────
g_deg = np.array(h.g_angles)
g_rad = np.deg2rad(g_deg)

# ── Intensity data (cd/klm) ───────────────────────────────────────────────────
i_c0   = get_plane(0.0)
i_c90  = get_plane(90.0)
i_c180 = get_plane(180.0)
i_c270 = get_plane(270.0)

print(f"\nI(C=0°,   γ=0°) = {i_c0[0]:.2f} cd/klm")
print(f"I(C=90°,  γ=0°) = {i_c90[0]:.2f} cd/klm")
print(f"I(C=180°, γ=0°) = {i_c180[0]:.2f} cd/klm")
print(f"I(C=270°, γ=0°) = {i_c270[0]:.2f} cd/klm")

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(6, 6))

# γ=0° at bottom, angles increase counter-clockwise
# → +g_rad (C=0° and C=90°)  lands on the RIGHT half
# → -g_rad (C=180° and C=270°) lands on the LEFT half
ax.set_theta_zero_location("S")
ax.set_theta_direction(1)

# C=0° and C=180° — solid lines
ax.plot( g_rad, i_c0,   color="#1f77b4", linewidth=1.5, linestyle="-",  label="C=0°")
ax.plot(-g_rad, i_c180, color="#d62728", linewidth=1.5, linestyle="-",  label="C=180°")

# C=90° and C=270° — dashed lines
ax.plot( g_rad, i_c90,  color="#2ca02c", linewidth=1.5, linestyle="--", label="C=90°")
ax.plot(-g_rad, i_c270, color="#ff7f0e", linewidth=1.5, linestyle="--", label="C=270°")

# Title and legend
ax.set_title(f"{h.luminaire_name}\n{h.company}", pad=16, fontsize=10)
ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=9)

# Radial labels on the 0° axis (bottom), with unit
ax.set_rlabel_position(0)

# Place "cd/klm" just below the outermost radial tick, on the 0° axis
r_max = ax.get_rmax()
ax.text(
    np.deg2rad(0), r_max * 1.15,   # angle=0° (bottom), just outside the last tick
    "cd/klm",
    ha="center", va="center",
    fontsize=8, color="gray"
)

# Angular tick labels: γ values symmetric around the vertical axis
tick_angles_mpl = [0, 45, 90, 135, 180, 225, 270, 315]
tick_labels     = ["0°", "45°", "90°", "135°", "180°", "135°", "90°", "45°"]
ax.set_thetagrids(tick_angles_mpl, labels=tick_labels)

plt.tight_layout()
plt.savefig("examples/02_polar_diagram.png", dpi=150)
print("\nDiagram saved to examples/02_polar_diagram.png")
plt.show()
