"""
freecad_utils.py — Shared FreeCAD utility library for generators

Installed to: Macro/_lib/freecad_utils.py
Imported by:  brick_generator_macro, radial_brick_generator_macro,
              clapboard_generator, board_batten_generator, bead_board_generator,
              shingle_generator, smart_trim_generator, station_sign_generator

Version: 1.0.1
"""

__version__ = "1.0.1"


# ---------------------------------------------------------------------------
# Global placement helpers
# ---------------------------------------------------------------------------

def get_global_face(obj, face_index):
    """
    Return a face from *obj* in global (world) coordinates.

    When an object lives inside a Part container with a non-identity
    Placement, ``obj.Shape.Faces[i]`` gives local coordinates only.
    This function applies the global placement transform so the returned
    face is correctly positioned in world space.

    Parameters
    ----------
    obj : FreeCAD document object
        Must have a ``Shape`` attribute.
    face_index : int
        Zero-based index into ``obj.Shape.Faces``.

    Returns
    -------
    Part.Face
        Face geometry in global coordinates.

    Raises
    ------
    IndexError
        If *face_index* is out of range for this object's faces.
    """
    face = obj.Shape.Faces[face_index]
    try:
        placement = obj.getGlobalPlacement()
        if not placement.isIdentity():
            # transformGeometry() returns Part.Shape, not Part.Face.
            # .Faces[0] recovers the proper Part.Face (with .Surface etc.)
            face = face.transformGeometry(placement.toMatrix()).Faces[0]
    except AttributeError:
        pass  # Object doesn't support getGlobalPlacement (e.g. Sketch)
    return face


def get_global_placement_matrix(obj):
    """
    Return the global placement matrix for *obj*, or None if unavailable.

    Useful when you want to log or reuse the matrix without calling
    ``getGlobalPlacement()`` twice.

    Parameters
    ----------
    obj : FreeCAD document object

    Returns
    -------
    FreeCAD.Matrix or None
        None if the object doesn't support ``getGlobalPlacement()``.
    """
    try:
        return obj.getGlobalPlacement().toMatrix()
    except AttributeError:
        return None


def object_has_global_offset(obj):
    """
    Return True if *obj* is inside a Part container with a non-identity
    placement (i.e. its local and global coordinate frames differ).

    Parameters
    ----------
    obj : FreeCAD document object

    Returns
    -------
    bool
    """
    try:
        return not obj.getGlobalPlacement().isIdentity()
    except AttributeError:
        return False


def log_global_placement(obj, label=None):
    """
    Print a one-line diagnostic if *obj* has a non-identity global
    placement.  Silent if placement is identity.

    Parameters
    ----------
    obj : FreeCAD document object
    label : str, optional
        Prefix shown in the message (defaults to obj.Label).
    """
    name = label or getattr(obj, 'Label', repr(obj))
    try:
        p = obj.getGlobalPlacement()
        if not p.isIdentity():
            pos = p.Base
            print(f"  NOTE: {name} is in a Part container — "
                  f"global placement offset ({pos.x:.3f}, {pos.y:.3f}, {pos.z:.3f}) "
                  f"will be applied to face geometry")
    except AttributeError:
        pass
