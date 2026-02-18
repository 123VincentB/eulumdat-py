"""
Writer for EULUMDAT (.ldt) photometric files.
"""

from __future__ import annotations
from pathlib import Path
from typing import List

from .model import Ldt, LdtHeader


class LdtWriter:
    """
    Writer for EULUMDAT (.ldt) files.

    Handles optional symmetry compression and safe file naming
    (auto-increments filename if destination already exists).

    Example:
        >>> from pyldt import LdtReader, LdtWriter
        >>> ldt = LdtReader.read("input.ldt")
        >>> ldt.header.luminaire_name = "Modified luminaire"
        >>> saved = LdtWriter.write(ldt, "output.ldt")
        >>> print(f"Saved to: {saved}")
    """

    @staticmethod
    def _fmt(x) -> str:
        """Format a number cleanly (no trailing zeros)."""
        if isinstance(x, str):
            return x
        if isinstance(x, int):
            return str(x)
        s = ("%.6f" % float(x)).rstrip("0").rstrip(".")
        return "0" if s == "-0" else s

    @staticmethod
    def _find_unique_path(path: Path) -> Path:
        """Return a unique path by appending _1, _2, ... if the file exists."""
        if not path.exists():
            return path
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        index = 1
        while True:
            new_path = parent / f"{stem}_{index}{suffix}"
            if not new_path.exists():
                return new_path
            index += 1

    @staticmethod
    def _compress_matrix(h: LdtHeader, full: List[List[float]]) -> List[List[float]]:
        """Compress the full intensity matrix according to ISYM for file storage."""
        mc, ng = h.mc, h.ng

        if h.isym == 0:
            return full

        elif h.isym == 1:
            return [full[0]]

        elif h.isym == 2:
            half = mc // 2 + 1
            return full[:half]

        elif h.isym == 3:
            # C90-C270 symmetry: specific storage order (C270 down to C90)
            step = 360.0 / mc if mc else 0.0
            angle_to_idx = {round(a % 360.0, 6): i
                            for i, a in enumerate(h.c_angles)} if h.c_angles else {}

            def idx_for_angle(a):
                a = round(a % 360.0, 6)
                return angle_to_idx.get(a, int(round((a / 360.0) * mc)) % mc)

            n = mc // 2 + 1
            start = 270.0
            indices = [idx_for_angle(start - k * step) for k in range(n)]
            return [full[i] for i in indices]

        elif h.isym == 4:
            q = mc // 4 + 1
            return full[:q]

        return full

    @classmethod
    def write(cls, ldt: Ldt, path: str | Path,
              compress_symmetry: bool = True,
              compress_header: bool = False,
              overwrite: bool = False) -> Path:
        """
        Save an Ldt object to an EULUMDAT file.

        Args:
            ldt: Ldt object to save.
            path: Destination file path.
            compress_symmetry: If True (default), compress the intensity matrix
                according to ISYM before writing.
            compress_header: If True, also adjust the mc value in the header
                to match the compressed matrix. Use only if the reader is
                expected to handle the compressed form.
            overwrite: If False (default), append _1, _2, ... to the filename
                if the destination already exists.

        Returns:
            Effective path where the file was saved.

        Raises:
            ValueError: If the intensity matrix dimensions do not match the header.
        """
        path = Path(path)

        if not overwrite:
            path = cls._find_unique_path(path)

        h = ldt.header
        mc, ng = h.mc, h.ng

        if len(ldt.intensities) != mc or any(len(r) != ng for r in ldt.intensities):
            raise ValueError(
                f"Intensity matrix must be [{mc} x {ng}], "
                f"got [{len(ldt.intensities)} x {len(ldt.intensities[0]) if ldt.intensities else 0}]"
            )

        lines = []

        # Lines 1-12 : Identification
        lines.append(h.company)
        lines.append(str(h.ityp))
        lines.append(str(h.isym))

        # Line 4 : mc (optionally adjusted for compressed header)
        if compress_header and compress_symmetry:
            if h.isym == 1:
                mc_write = 1
            elif h.isym == 2:
                mc_write = mc // 2 + 1
            elif h.isym == 3:
                mc_write = mc // 2 + 1
            elif h.isym == 4:
                mc_write = mc // 4 + 1
            else:
                mc_write = mc
            lines.append(str(mc_write))
        else:
            lines.append(str(mc))

        dc_write = 360.0 if (compress_header and compress_symmetry and h.isym == 1) else h.dc
        lines.append(cls._fmt(dc_write))

        lines.append(str(ng))
        lines.append(cls._fmt(h.dg))
        lines.append(h.report_number)
        lines.append(h.luminaire_name)
        lines.append(h.luminaire_number)
        lines.append(h.file_name)
        lines.append(h.date_user)

        # Lines 13-22 : Geometry
        lines.append(cls._fmt(h.length))
        lines.append(cls._fmt(h.width))
        lines.append(cls._fmt(h.height))
        lines.append(cls._fmt(h.length_lum_area))
        lines.append(cls._fmt(h.width_lum_area))
        lines.append(cls._fmt(h.h_lum_c0))
        lines.append(cls._fmt(h.h_lum_c90))
        lines.append(cls._fmt(h.h_lum_c180))
        lines.append(cls._fmt(h.h_lum_c270))

        # Lines 23-26 : Photometric factors
        lines.append(cls._fmt(h.dff))
        lines.append(cls._fmt(h.lorl))
        lines.append(cls._fmt(h.conv_factor))
        lines.append(cls._fmt(h.tilt))

        # Lamp sets
        lines.append(str(h.n_sets))
        n = max(1, h.n_sets)

        num_lamps = (h.num_lamps + [0] * n)[:n]
        lamp_types = (h.lamp_types + [""] * n)[:n]
        lamp_flux = (h.lamp_flux + [0.0] * n)[:n]
        lamp_cct = (h.lamp_cct + [""] * n)[:n]
        lamp_cri = (h.lamp_cri + [""] * n)[:n]
        lamp_watt = (h.lamp_watt + [0.0] * n)[:n]

        lines.append(" ".join(str(v) for v in num_lamps))
        lines.append(" ".join(lamp_types))
        lines.append(" ".join(cls._fmt(v) for v in lamp_flux))
        lines.append(" ".join(lamp_cct))
        lines.append(" ".join(lamp_cri))
        lines.append(" ".join(cls._fmt(v) for v in lamp_watt))

        # Direct ratios (10 values)
        dr = (h.direct_ratios + [0.0] * 10)[:10]
        for val in dr:
            lines.append(cls._fmt(val))

        # Reconstruct angle arrays if missing
        c_full = h.c_angles if (h.c_angles and len(h.c_angles) == mc) else \
            [i * h.dc for i in range(mc)] if h.dc > 0 else \
            [i * 360.0 / mc for i in range(mc)]

        g_full = h.g_angles if (h.g_angles and len(h.g_angles) == ng) else \
            [i * h.dg for i in range(ng)] if h.dg > 0 else \
            [i * 180.0 / (ng - 1) for i in range(ng)] if ng > 1 else [0.0]

        # C-angles (compressed or full)
        if compress_symmetry and compress_header:
            if h.isym == 3:
                step = 360.0 / mc if mc else 0.0
                angle_to_idx = {round(a % 360.0, 6): i for i, a in enumerate(c_full)}

                def idx_for_angle(a):
                    a = round(a % 360.0, 6)
                    return angle_to_idx.get(a, int(round((a / 360.0) * mc)) % mc)

                n_c = mc // 2 + 1
                start = 270.0
                indices = [idx_for_angle(start - k * step) for k in range(n_c)]
                for idx in indices:
                    lines.append(cls._fmt(c_full[idx]))
            else:
                matrix_compressed = cls._compress_matrix(h, ldt.intensities)
                for i in range(len(matrix_compressed)):
                    lines.append(cls._fmt(c_full[i]))
        else:
            for angle in c_full:
                lines.append(cls._fmt(angle))

        # Gamma angles (always full)
        for angle in g_full:
            lines.append(cls._fmt(angle))

        # Intensity data
        matrix = cls._compress_matrix(h, ldt.intensities) if compress_symmetry else ldt.intensities
        for row in matrix:
            for val in row:
                lines.append(cls._fmt(val))

        # Write in ISO-8859-1 (EULUMDAT standard encoding)
        path.write_text("\n".join(lines) + "\n", encoding="iso-8859-1", errors="replace")

        return path
