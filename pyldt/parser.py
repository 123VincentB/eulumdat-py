"""
Parser for EULUMDAT (.ldt) photometric files.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Tuple

from .model import Ldt, LdtHeader


# ---------- Parsing utilities ----------

def _to_float(s: str) -> float:
    """Convert string to float, handling commas and empty values."""
    s = (s or "").strip().replace(",", ".")
    return 0.0 if s == "" else float(s)


def _to_int(s: str) -> int:
    """Convert string to int via float (handles various formats)."""
    return int(float(_to_float(s)))


def _split_floats(line: str) -> List[float]:
    """Split a line into a list of floats."""
    return [_to_float(t) for t in line.split()]


# ---------- Reader ----------

class LdtReader:
    """
    Robust parser for EULUMDAT (.ldt) files.

    Handles all symmetry types (ISYM 0-4) and expands the intensity
    matrix to the full angular range by default.

    Example:
        >>> from pyldt import LdtReader
        >>> ldt = LdtReader.read("luminaire.ldt")
        >>> print(ldt.header.luminaire_name)
        >>> print(ldt.intensities[0][0])  # cd/klm at C=0°, γ=0°
    """

    @staticmethod
    def _mc_range_from_isym(isym: int, mc: int) -> Tuple[int, int]:
        """Return the range of C-planes stored in the file based on symmetry."""
        if mc <= 0:
            return (1, 0)
        if isym == 0:
            return (1, mc)
        if isym == 1:
            return (1, 1)
        if isym == 2:
            return (1, mc // 2 + 1)
        if isym == 3:
            return (1, mc // 2 + 1)
        if isym == 4:
            return (1, mc // 4 + 1)
        return (1, mc)

    @staticmethod
    def _expand_to_full_matrix(h: LdtHeader, ser: List[List[float]]) -> List[List[float]]:
        """Expand a symmetry-compressed matrix to the full [mc x ng] matrix."""
        mc, ng = h.mc, h.ng
        full = [[0.0] * ng for _ in range(mc)]

        def copy_row(ci, si):
            full[ci] = list(ser[si])

        if h.isym == 0:
            for i in range(mc):
                copy_row(i, i)

        elif h.isym == 1:
            for i in range(mc):
                copy_row(i, 0)

        elif h.isym == 2:
            # Symmetry about vertical plane C0-C180
            half = mc // 2 + 1
            for i in range(half):
                copy_row(i, i)
            for k in range(1, mc - half + 1):
                full[half - 1 + k] = list(full[half - k])

        elif h.isym == 3:
            # Symmetry about plane C90-C270
            # File stores planes from C270 down to C90 (decreasing order)
            step = 360.0 / mc if mc else 0.0
            angle_to_idx = {round(a % 360.0, 6): i
                            for i, a in enumerate(h.c_angles)} if h.c_angles else {}

            def idx_for_angle(a):
                a = round(a % 360.0, 6)
                return angle_to_idx.get(a, int(round((a / 360.0) * mc)) % mc)

            n = mc // 2 + 1
            start = 270.0  # Starts at C270
            order = [idx_for_angle(start - k * step) for k in range(n)]

            for si, ci in enumerate(order):
                copy_row(ci, si)

            # Fill missing planes by symmetry
            for k in range(mc):
                if full[k] == [0.0] * ng:
                    full[k] = list(full[(k + mc // 2) % mc])

        elif h.isym == 4:
            # Quadrant symmetry
            q = mc // 4 + 1
            for i in range(q):
                copy_row(i, i)
            for k in range(1, mc // 4):
                full[q - 1 + k] = list(full[q - 1 - k])
            base = mc // 2
            for k in range(q):
                full[base + k] = list(full[k])
            for k in range(1, mc // 4):
                full[base + q - 1 + k] = list(full[base + q - 1 - k])

        return full

    @classmethod
    def read(cls, path: str | Path, *, expand_symmetry: bool = True) -> Ldt:
        """
        Load an EULUMDAT file from disk.

        Args:
            path: Path to the .ldt file.
            expand_symmetry: If True (default), expand the intensity matrix
                to the full angular range according to ISYM. If False, return
                only the planes stored in the file.

        Returns:
            Ldt object containing header metadata and intensity matrix.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file cannot be parsed.
        """
        path = Path(path)
        raw = path.read_bytes()
        if raw[:3] == b"\xef\xbb\xbf":  # UTF-8 BOM
            raw = raw[3:]
        text = raw.decode("latin-1")
        lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        i = 0

        def pop_raw():
            """Return the next line as-is (preserves empty lines for text fields)."""
            nonlocal i
            if i >= len(lines):
                return ""
            v = lines[i].strip()
            i += 1
            return v

        def pop():
            """Return the next non-empty line (for numeric fields)."""
            nonlocal i
            v = ""
            while i < len(lines) and v == "":
                v = lines[i].strip()
                i += 1
            return v

        def pop_n_numbers(n):
            """Collect n numbers, possibly spanning multiple lines."""
            nonlocal i
            vals = []
            while len(vals) < n and i < len(lines):
                ln = lines[i].strip()
                i += 1
                if ln:
                    vals.extend(_split_floats(ln))
            return vals[:n]

        h = LdtHeader()

        # Lines 1-12 : Identification (pop_raw: empty lines are valid values)
        h.company = pop_raw()
        h.ityp = _to_int(pop_raw())
        h.isym = _to_int(pop_raw())
        h.mc = _to_int(pop_raw())
        h.dc = _to_float(pop_raw())
        h.ng = _to_int(pop_raw())
        h.dg = _to_float(pop_raw())
        h.report_number = pop_raw()
        h.luminaire_name = pop_raw()
        h.luminaire_number = pop_raw()   # can be empty string
        h.file_name = pop_raw()
        h.date_user = pop_raw()

        # Lines 13-22 : Geometry
        h.length = _to_float(pop())
        h.width = _to_float(pop())
        h.height = _to_float(pop())
        h.length_lum_area = _to_float(pop())
        h.width_lum_area = _to_float(pop())
        h.h_lum_c0 = _to_float(pop())
        h.h_lum_c90 = _to_float(pop())
        h.h_lum_c180 = _to_float(pop())
        h.h_lum_c270 = _to_float(pop())

        # Lines 23-26 : Photometric factors
        h.dff = _to_float(pop())
        h.lorl = _to_float(pop())
        h.conv_factor = _to_float(pop())
        h.tilt = _to_float(pop())

        # Lamp sets — interpretation B: 6 lines per set
        # For N sets: set 1 (lines 27-32), set 2 (lines 33-38), etc.
        h.n_sets = _to_int(pop())
        n = max(1, h.n_sets)

        h.num_lamps = []
        h.lamp_types = []
        h.lamp_flux = []
        h.lamp_cct = []
        h.lamp_cri = []
        h.lamp_watt = []

        for _ in range(n):
            h.num_lamps.append(_to_int(pop_raw()))
            h.lamp_types.append(pop_raw())
            h.lamp_flux.append(_to_float(pop_raw()))
            h.lamp_cct.append(pop_raw())
            h.lamp_cri.append(pop_raw())
            h.lamp_watt.append(_to_float(pop_raw()))

        # Direct ratios (10 values)
        h.direct_ratios = pop_n_numbers(10)
        if len(h.direct_ratios) < 10:
            h.direct_ratios += [0.0] * (10 - len(h.direct_ratios))

        # Angular grids
        h.c_angles = pop_n_numbers(h.mc)
        h.g_angles = pop_n_numbers(h.ng)

        # Intensity data (symmetry-compressed in file)
        mc1, mc2 = cls._mc_range_from_isym(h.isym, h.mc)
        n_ser = (h.mc // 2 + 1) if h.isym == 3 else (mc2 - mc1 + 1)

        vals = pop_n_numbers(n_ser * h.ng)
        ser = [vals[r * h.ng:(r + 1) * h.ng] for r in range(n_ser)]

        intensities = cls._expand_to_full_matrix(h, ser) if expand_symmetry else ser

        return Ldt(header=h, intensities=intensities, filepath=path)
