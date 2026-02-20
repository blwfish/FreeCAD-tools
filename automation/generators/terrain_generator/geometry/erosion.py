# Erosion Feature Generation
# Undercuts, drainage lines, caves, and other erosion features.

import numpy as np
from typing import List, Optional, Tuple


class ErosionGenerator:
    """Generate erosion features on terrain heightmaps.

    Creates geologically-plausible erosion patterns including:
    - Undercut banks (river erosion)
    - Drainage lines (water erosion channels)
    - Natural ledges/benches (differential weathering)
    """

    def __init__(self, rng: Optional[np.random.Generator] = None):
        self.rng = rng or np.random.default_rng()

    def add_drainage_lines(
        self,
        heightmap: np.ndarray,
        resolution: float,
        num_lines: int = 3,
        depth: float = 0.05,
        width: float = 0.1,
        direction: str = "downslope",
    ) -> np.ndarray:
        """Add water erosion drainage channels.

        Args:
            heightmap: 2D elevation array
            resolution: Grid spacing in inches
            num_lines: Number of drainage channels
            depth: Maximum channel depth in inches
            width: Channel width in inches
            direction: "downslope" (follow gradient) or "vertical" (Y direction)

        Returns:
            Modified heightmap with drainage channels
        """
        result = heightmap.copy()
        rows, cols = result.shape

        width_cells = max(2, int(width / resolution))

        for _ in range(num_lines):
            if direction == "vertical":
                # Simple vertical channel with random X wander
                x_start = self.rng.integers(cols // 4, 3 * cols // 4)
                x_pos = float(x_start)

                for i in range(rows):
                    x_int = int(np.clip(x_pos, 0, cols - 1))
                    # Carve channel cross-section
                    for dx in range(-width_cells, width_cells + 1):
                        xi = x_int + dx
                        if 0 <= xi < cols:
                            dist = abs(dx) / max(width_cells, 1)
                            carve = depth * (1.0 - dist)
                            result[i, xi] -= max(carve, 0)

                    # Random walk
                    x_pos += self.rng.normal(0, 0.3)
                    x_pos = np.clip(x_pos, 1, cols - 2)
            else:
                # Follow steepest descent
                x_pos = float(self.rng.integers(cols // 4, 3 * cols // 4))
                y_pos = 0.0

                visited = set()
                while 0 <= int(y_pos) < rows - 1 and 0 <= int(x_pos) < cols - 1:
                    yi, xi = int(y_pos), int(x_pos)
                    if (yi, xi) in visited:
                        break
                    visited.add((yi, xi))

                    # Carve at current position
                    for dx in range(-width_cells, width_cells + 1):
                        xj = xi + dx
                        if 0 <= xj < cols:
                            dist = abs(dx) / max(width_cells, 1)
                            carve = depth * (1.0 - dist)
                            result[yi, xj] -= max(carve, 0)

                    # Find steepest descent among neighbors
                    best_dy, best_dx = 1, 0
                    best_drop = -np.inf
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dy == 0 and dx == 0:
                                continue
                            ny, nx = yi + dy, xi + dx
                            if 0 <= ny < rows and 0 <= nx < cols:
                                drop = heightmap[yi, xi] - heightmap[ny, nx]
                                if drop > best_drop:
                                    best_drop = drop
                                    best_dy, best_dx = dy, dx

                    y_pos += best_dy
                    x_pos += best_dx + self.rng.normal(0, 0.2)
                    x_pos = np.clip(x_pos, 0, cols - 1)

        return result

    def add_ledges(
        self,
        heightmap: np.ndarray,
        resolution: float,
        num_ledges: int = 2,
        ledge_width: float = 0.3,
        ledge_depth: float = 0.1,
    ) -> np.ndarray:
        """Add natural ledges/benches from differential weathering.

        Creates horizontal step features at random elevations,
        typical of layered sedimentary rock.

        Args:
            heightmap: 2D elevation array
            resolution: Grid spacing in inches
            num_ledges: Number of ledge features
            ledge_width: Width of ledge flat area in inches
            ledge_depth: Step depth at ledge front in inches

        Returns:
            Modified heightmap
        """
        result = heightmap.copy()
        rows, cols = result.shape

        z_min = np.min(heightmap)
        z_max = np.max(heightmap)
        z_range = z_max - z_min

        if z_range < 0.1:
            return result

        # Place ledges at random elevations
        for _ in range(num_ledges):
            ledge_z = z_min + self.rng.uniform(0.2, 0.8) * z_range
            width_cells = max(2, int(ledge_width / resolution))

            # Find cells near this elevation
            near_elevation = np.abs(heightmap - ledge_z) < ledge_width * 0.5

            # Create a flattened band
            for i in range(rows):
                for j in range(cols):
                    if near_elevation[i, j]:
                        # Flatten to ledge elevation with slight inward step
                        result[i, j] = min(result[i, j], ledge_z)

        return result

    def add_undercut(
        self,
        heightmap: np.ndarray,
        resolution: float,
        side: str = "left",
        undercut_depth: float = 0.3,
        undercut_height: float = 0.5,
        elevation: float = 0.0,
    ) -> np.ndarray:
        """Mark undercut regions on the heightmap.

        Note: True undercuts can't be represented in a pure heightmap
        (single Z per XY). This method creates a steep overhang effect
        by locally steepening the slope. For actual undercuts, the mesh
        must be generated as a full 3D mesh (not heightmap-based).

        For 4th-axis CNC: the mesh_utils module can split geometry for
        multi-setup machining.

        Args:
            heightmap: 2D elevation array
            resolution: Grid spacing in inches
            side: "left" or "right" (which side gets the undercut)
            undercut_depth: How far the undercut extends horizontally
            undercut_height: Vertical extent of the undercut
            elevation: Base elevation of the undercut

        Returns:
            Modified heightmap (steepened at undercut location)
        """
        result = heightmap.copy()
        rows, cols = result.shape

        depth_cells = max(1, int(undercut_depth / resolution))

        for i in range(rows):
            if side == "left":
                # Steepen the left edge
                for j in range(min(depth_cells, cols)):
                    z = result[i, j]
                    if elevation <= z <= elevation + undercut_height:
                        # Pull inward (steepen)
                        t = j / depth_cells
                        result[i, j] = elevation + (z - elevation) * (t ** 0.3)
            else:
                # Steepen the right edge
                for j in range(max(0, cols - depth_cells), cols):
                    z = result[i, j]
                    t_from_edge = (cols - 1 - j) / depth_cells
                    if elevation <= z <= elevation + undercut_height:
                        result[i, j] = elevation + (z - elevation) * (t_from_edge ** 0.3)

        return result
