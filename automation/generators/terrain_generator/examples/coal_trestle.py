#!/usr/bin/env python3
"""Example: Coal Trestle Hillside (UC1)

Generates a terrain substrate for a C&O coal trestle and loading facility.
The hillside has sandstone jointing, rises from 2" to 8", and fits a
12" x 18" footprint.

Usage:
    python -m terrain_generator.examples.coal_trestle
    # or
    python terrain_generator/examples/coal_trestle.py

Output:
    coal_trestle_terrain.stl   - CNC-ready mesh
    coal_trestle_terrain_metadata.json - Generation metadata
"""

import os
import sys

# Add parent directory to path for standalone execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from terrain_generator import TerrainGenerator


def main():
    # Coal trestle hillside parameters (UC1 from spec)
    params = {
        "feature_type": "hillside",
        "dimensions": {
            "width_inches": 12.0,
            "length_inches": 18.0,
            "height_inches": 6.0,
            "material_depth_inches": 2.0,
        },
        "geometry": {
            "base_elevation": 2.0,
            "peak_elevation": 8.0,
            "slope_angle_dominant": 0.0,    # Slope rises along Y axis
            "slope_angle_variance": 5.0,
        },
        "geology": {
            "rock_type": "sandstone",
            "jointing_angle_primary": 60.0,  # Dominant 60° bedding angle
            "jointing_spacing": 1.5,          # ~1.5" between visible joints at HO
            "jointing_spacing_variance": 0.2,
            "weathering_intensity": 0.4,      # Moderate weathering
            "erosion_features": ["drainage_lines"],
        },
        "material": "xps_foam",
        "cnc_constraints": {
            "max_tool_diameter": 0.25,
            "max_depth_per_pass": 0.25,
            "surface_finish": "detail",
        },
        "resolution": 0.05,    # 0.05" grid (fine detail)
        "seed": 42,            # Reproducible
    }

    # Output directory
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "coal_trestle_terrain.stl")

    print("Generating coal trestle hillside terrain...")
    print(f"  Feature: {params['feature_type']}")
    print(f"  Dimensions: {params['dimensions']['width_inches']}\" x {params['dimensions']['length_inches']}\"")
    print(f"  Relief: {params['geometry']['base_elevation']}\" to {params['geometry']['peak_elevation']}\"")
    print(f"  Rock type: {params['geology']['rock_type']}")
    print(f"  Seed: {params['seed']}")
    print()

    gen = TerrainGenerator(seed=params["seed"])
    result = gen.generate(params, export_path=out_path)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        if result.get("validation", {}).get("errors"):
            for e in result["validation"]["errors"]:
                print(f"  - {e}")
        return 1

    # Print results
    stats = result["mesh_stats"]
    print(f"Generation complete in {result['generation_time_sec']:.2f}s")
    print(f"  Vertices: {stats['vertex_count']:,}")
    print(f"  Faces: {stats['face_count']:,}")
    bb = stats["bounding_box"]
    print(f"  Bounding box: {bb[0]:.2f} x {bb[1]:.2f} x {bb[2]:.2f} inches")
    print(f"  Valid: {stats['valid']}")

    if stats.get("issues"):
        print("  Issues:")
        for issue in stats["issues"]:
            print(f"    - {issue}")

    if result.get("validation", {}).get("warnings"):
        print("  Warnings:")
        for w in result["validation"]["warnings"]:
            print(f"    - {w}")

    if result.get("export"):
        exp = result["export"]
        print(f"\nExported:")
        print(f"  Mesh: {exp['mesh_file']} ({exp['mesh_size_bytes']/1024:.1f} KB)")
        print(f"  Metadata: {exp['metadata_file']}")

    # Also generate a quick preview for comparison
    print("\n--- Quick Preview (4x coarser) ---")
    preview = gen.generate_preview(params)
    ps = preview["mesh_stats"]
    print(f"  Vertices: {ps['vertex_count']:,}, Faces: {ps['face_count']:,}")
    print(f"  Time: {preview['generation_time_sec']:.2f}s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
