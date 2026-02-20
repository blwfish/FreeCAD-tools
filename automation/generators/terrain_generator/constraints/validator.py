# Constraint Validator
# Validates terrain specifications for feasibility before generation.

from typing import Dict, Any, List, Optional
from .geology_knowledge import GeologyKnowledge


class ConstraintValidator:
    """Validate terrain specifications for physical and CNC feasibility.

    Checks dimensional limits, geological plausibility, CNC tool access,
    and material compatibility. Returns detailed error/warning messages.
    """

    # Genmitsu 4030 ProVerXL2 working limits
    CNC_MAX_X = 15.7  # inches (~400mm)
    CNC_MAX_Y = 11.8  # inches (~300mm)
    CNC_MAX_Z = 3.0   # inches (~75mm) safe Z travel

    @staticmethod
    def validate(spec: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a terrain specification.

        Args:
            spec: Fully-resolved terrain specification (from ConstraintParser)

        Returns:
            Dict with:
            - valid: bool
            - errors: list of blocking error strings
            - warnings: list of non-blocking warning strings
        """
        errors = []
        warnings = []

        dims = spec.get("dimensions", {})
        geom = spec.get("geometry", {})
        geo = spec.get("geology", {})
        cnc = spec.get("cnc_constraints", {})
        material = spec.get("material", "xps_foam")

        # --- Dimensional checks ---
        width = dims.get("width_inches", 0)
        length = dims.get("length_inches", 0)
        height = dims.get("height_inches", 0)
        mat_depth = dims.get("material_depth_inches", 0)

        if width <= 0 or length <= 0 or height <= 0:
            errors.append("All dimensions must be positive")

        if width > ConstraintValidator.CNC_MAX_X:
            warnings.append(
                f"Width {width}\" exceeds CNC X travel ({ConstraintValidator.CNC_MAX_X}\"). "
                "May need to split into modular sections or reposition workpiece."
            )

        if length > ConstraintValidator.CNC_MAX_Y:
            warnings.append(
                f"Length {length}\" exceeds CNC Y travel ({ConstraintValidator.CNC_MAX_Y}\"). "
                "May need to split into modular sections or reposition workpiece."
            )

        if height > ConstraintValidator.CNC_MAX_Z:
            warnings.append(
                f"Height {height}\" exceeds safe CNC Z travel ({ConstraintValidator.CNC_MAX_Z}\"). "
                "Multi-layer approach required (stack foam sheets)."
            )

        if mat_depth <= 0:
            errors.append("Material depth must be positive")
        elif height > mat_depth * 3:
            warnings.append(
                f"Height {height}\" vs material depth {mat_depth}\": "
                "will need 3+ stacked layers. Consider deeper material or reduced height."
            )

        # --- Geometry checks ---
        base_elev = geom.get("base_elevation", 0)
        peak_elev = geom.get("peak_elevation", 0)

        if peak_elev <= base_elev:
            errors.append(f"Peak elevation ({peak_elev}\") must be greater than base ({base_elev}\")")

        relief = peak_elev - base_elev
        if relief > height * 1.1:
            warnings.append(
                f"Relief ({relief}\") exceeds specified height ({height}\"). "
                "Heightmap will be clipped."
            )

        # --- Geological checks ---
        rock_type = geo.get("rock_type", "sandstone")
        try:
            rt = GeologyKnowledge.get_rock_type(rock_type)
        except ValueError as e:
            errors.append(str(e))
            rt = None

        if rt:
            angle = geo.get("jointing_angle_primary", 60)
            warning = GeologyKnowledge.validate_jointing_angle(rock_type, angle)
            if warning:
                warnings.append(warning)

            spacing = geo.get("jointing_spacing", 1.0)
            if spacing < 0.05:
                warnings.append(
                    f"Jointing spacing {spacing}\" is very fine. "
                    "May not be cuttable with available CNC tooling. "
                    f"Minimum tool diameter: {cnc.get('max_tool_diameter', 0.25)}\"."
                )

            spacing_ho = rt.jointing_spacing_ho_inches
            if spacing < spacing_ho[0] * 0.5:
                warnings.append(
                    f"Jointing spacing {spacing}\" is much finer than HO scale for {rock_type} "
                    f"({spacing_ho[0]:.2f}\"-{spacing_ho[1]:.2f}\"). Consider increasing for realism."
                )

        # --- CNC feasibility ---
        tool_dia = cnc.get("max_tool_diameter", 0.25)
        if tool_dia <= 0:
            errors.append("Tool diameter must be positive")

        # Check jointing is wide enough for tool
        spacing = geo.get("jointing_spacing", 1.0)
        joint_width = 0.02  # typical joint groove width
        if joint_width < tool_dia * 0.5:
            warnings.append(
                f"Joint groove width ({joint_width}\") is less than half the tool diameter "
                f"({tool_dia}\"). Joints may not be visible. Use a finer tool for engraving detail."
            )

        # Check erosion features vs CNC
        erosion_features = geo.get("erosion_features", [])
        if "cave_mouth" in erosion_features:
            warnings.append(
                "Cave mouth features require significant Z depth and may need "
                "4th-axis or multi-setup machining."
            )
        if "undercut_banks" in erosion_features:
            warnings.append(
                "Undercut banks cannot be machined with 3-axis CNC in a single setup. "
                "Consider 4th-axis attachment or multi-setup approach."
            )

        # --- Material checks ---
        try:
            mat = GeologyKnowledge.get_material(material)
            if height > mat_depth:
                passes_needed = int(height / mat.get("max_depth_per_pass_inches", 0.25)) + 1
                if passes_needed > 20:
                    warnings.append(
                        f"Material requires {passes_needed} CNC passes. Consider deeper material."
                    )
        except ValueError as e:
            errors.append(str(e))

        # --- Resolution check ---
        resolution = spec.get("resolution", 0.05)
        total_cells = int(width / resolution) * int(length / resolution)
        if total_cells > 2_000_000:
            warnings.append(
                f"Resolution {resolution}\" produces {total_cells:,} grid cells. "
                "This may be slow to generate. Consider coarser resolution (0.1\")."
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
