"""
Basic usage example for pyldt.

This example demonstrates how to read an EULUMDAT file, inspect its content,
modify header fields, and save the result.

To run this example, provide a path to any valid .ldt file.
"""

from pathlib import Path
from pyldt import LdtReader, LdtWriter


def main():
    # --- Read ---
    input_path = Path("sample.ldt")   # Replace with your actual .ldt file path

    ldt = LdtReader.read(input_path)
    h = ldt.header

    print("=== Luminaire info ===")
    print(f"  Company        : {h.company}")
    print(f"  Luminaire name : {h.luminaire_name}")
    print(f"  Luminaire no.  : {h.luminaire_number}")
    print(f"  Date / User    : {h.date_user}")
    print(f"  Report no.     : {h.report_number}")

    print("\n=== Photometric data ===")
    print(f"  C-planes  : {h.mc}  (step {h.dc}°)")
    print(f"  γ-angles  : {h.ng}  (step {h.dg}°)")
    print(f"  ISYM      : {h.isym}")
    print(f"  LORL      : {h.lorl} %")
    print(f"  DFF       : {h.dff} %")

    print("\n=== Lamp sets ===")
    for k in range(h.n_sets):
        print(f"  Set {k+1}: {h.num_lamps[k]}x {h.lamp_types[k]}, "
              f"{h.lamp_flux[k]} lm, {h.lamp_watt[k]} W, "
              f"CCT={h.lamp_cct[k]}, CRI={h.lamp_cri[k]}")

    print("\n=== Sample intensities (cd/klm) ===")
    print(f"  C=0°,  γ=0°  : {ldt.intensities[0][0]:.1f}")
    print(f"  C=0°,  γ=90° : {ldt.intensities[0][-1]:.1f}")

    # --- Edit ---
    ldt.header.date_user = "2026-01-01 / demo"

    # --- Save ---
    output_path = input_path.parent / f"{input_path.stem}_modified.ldt"
    saved = LdtWriter.write(ldt, output_path, overwrite=False)
    print(f"\nSaved to: {saved}")

    # --- Round-trip verification ---
    ldt2 = LdtReader.read(saved)
    print(f"Verified name  : {ldt2.header.luminaire_name}")
    print(f"Verified I(0,0): {ldt2.intensities[0][0]:.1f} cd/klm")


if __name__ == "__main__":
    main()
