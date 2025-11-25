"""
FreeCAD TNP Error Decoder Package

Decode Topological Naming Problem (TNP) error messages from FreeCAD
into human-readable, actionable diagnostics.

Main functions:
    decode_tnp(error_string)        - Decode a single TNP error
    decode_tnp_batch(error_text)    - Decode multiple TNP errors
    scan_document_for_tnp()         - Scan active document for TNP issues

Example usage in FreeCAD Python console:
    from tnp_decoder import decode_tnp
    decode_tnp("Sketch004.e2 missing reference: Sketch003.;e7v2;SKT")
"""

# Single source of truth for version
__version__ = "1.0.0"
__author__ = "Model Railroading Community"
__license__ = "MIT"

from .decode_tnp import (
    TNPError,
    parse_error_line,
    decode_tnp,
    decode_tnp_batch,
    scan_document_for_tnp
)

__all__ = [
    'TNPError',
    'parse_error_line',
    'decode_tnp',
    'decode_tnp_batch',
    'scan_document_for_tnp',
]
