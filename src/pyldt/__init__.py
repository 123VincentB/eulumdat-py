"""
pyldt - Python library for reading and writing EULUMDAT (.ldt) photometric files.

Basic usage::

    from pyldt import LdtReader, LdtWriter

    # Read
    ldt = LdtReader.read("luminaire.ldt")
    print(ldt.header.luminaire_name)
    print(ldt.intensities[0][0])  # cd/klm at C=0°, γ=0°

    # Edit
    ldt.header.luminaire_name = "Modified"

    # Save
    LdtWriter.write(ldt, "output.ldt")
"""

from .model import Ldt, LdtHeader
from .parser import LdtReader
from .writer import LdtWriter

__version__ = "0.1.0"
__author__ = "123VincentB"
__license__ = "MIT"

__all__ = [
    "Ldt",
    "LdtHeader",
    "LdtReader",
    "LdtWriter",
]
