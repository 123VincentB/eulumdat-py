"""
Data model for EULUMDAT (.ldt) photometric files.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class LdtHeader:
    """
    EULUMDAT file header (lines 1-42 + direct ratios + angles).

    References:
        EULUMDAT Format Description, LiTG (Deutsche Lichttechnische Gesellschaft), 1990.
    """

    # Lines 1-12 : Identification
    company: str = ""
    ityp: int = 0           # Luminaire type (0=point, 1=linear, 2=area)
    isym: int = 0           # Symmetry (0=none, 1=full, 2=C0-C180, 3=C90-C270, 4=quadrant)
    mc: int = 0             # Number of C-planes
    dc: float = 0.0         # Angular step between C-planes (degrees)
    ng: int = 0             # Number of gamma angles per C-plane
    dg: float = 0.0         # Angular step between gamma angles (degrees)
    report_number: str = ""
    luminaire_name: str = ""
    luminaire_number: str = ""
    file_name: str = ""
    date_user: str = ""

    # Lines 13-22 : Geometry (mm)
    length: float = 0.0
    width: float = 0.0
    height: float = 0.0
    length_lum_area: float = 0.0
    width_lum_area: float = 0.0
    h_lum_c0: float = 0.0
    h_lum_c90: float = 0.0
    h_lum_c180: float = 0.0
    h_lum_c270: float = 0.0

    # Lines 23-26 : Photometric factors
    dff: float = 0.0        # Downward flux fraction (%)
    lorl: float = 0.0       # Light output ratio luminaire (%)
    conv_factor: float = 1.0
    tilt: float = 0.0

    # Line 26 : Number of lamp sets
    n_sets: int = 0

    # Lines 26a-26f : Lamp data (one entry per set)
    num_lamps: List[int] = field(default_factory=list)
    lamp_types: List[str] = field(default_factory=list)
    lamp_flux: List[float] = field(default_factory=list)
    lamp_cct: List[str] = field(default_factory=list)
    lamp_cri: List[str] = field(default_factory=list)
    lamp_watt: List[float] = field(default_factory=list)

    # Direct ratios (10 values, lines after lamp data)
    direct_ratios: List[float] = field(default_factory=list)

    # Angular grids
    c_angles: List[float] = field(default_factory=list)
    g_angles: List[float] = field(default_factory=list)


@dataclass
class Ldt:
    """
    Complete EULUMDAT file representation.

    Attributes:
        header: Parsed header with all metadata and lamp data.
        intensities: Full intensity matrix [mc x ng], in cd/klm.
            Always expanded to the full angular range regardless of file symmetry.
        filepath: Source file path (None if not loaded from disk).
    """
    header: LdtHeader
    intensities: List[List[float]]
    filepath: Optional[Path] = None
