# Input Handler
# Handles loading and preparing input data for terrain generation.
# Phase 1: structured parameter input only.
# Phase 2: reference photo analysis.
# Phase 3: natural language prompt parsing.

import json
import os
from typing import Dict, Any, Optional


class InputHandler:
    """Load and prepare terrain generation inputs.

    Phase 1 supports:
    - JSON parameter files
    - Python dict input
    - Basic reference photo path validation

    Future phases will add:
    - Photo analysis (jointing angle extraction)
    - Natural language prompt parsing
    - CAD model loading
    """

    @staticmethod
    def from_dict(params: Dict[str, Any]) -> Dict[str, Any]:
        """Pass through a parameter dict (already in correct format).

        Args:
            params: Raw terrain parameter dictionary

        Returns:
            Same dict (for consistency with other input methods)
        """
        return params

    @staticmethod
    def from_json_file(filepath: str) -> Dict[str, Any]:
        """Load terrain parameters from a JSON file.

        Args:
            filepath: Path to JSON parameter file

        Returns:
            Parsed parameter dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If file isn't valid JSON
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Parameter file not found: {filepath}")

        with open(filepath, 'r') as f:
            return json.load(f)

    @staticmethod
    def validate_reference_photos(params: Dict[str, Any]) -> list:
        """Check that referenced photo files exist.

        Args:
            params: Parameter dict with optional 'reference_photos' key

        Returns:
            List of warning strings for missing files
        """
        warnings = []
        photos = params.get("reference_photos", [])
        for photo in photos:
            path = photo.get("path", "")
            if path and not os.path.exists(path):
                warnings.append(f"Reference photo not found: {path}")
        return warnings
