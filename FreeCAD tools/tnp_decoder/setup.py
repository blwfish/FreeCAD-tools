"""
Setup configuration for freecad-tnp-decoder
"""

import os
from setuptools import setup, find_packages

# Read version from package __init__.py (single source of truth)
version = {}
with open(os.path.join(os.path.dirname(__file__), 'tnp_decoder', '__init__.py')) as f:
    for line in f:
        if line.startswith('__version__'):
            exec(line, version)
            break

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="freecad-tnp-decoder",
    version=version['__version__'],
    author="Model Railroading Community",
    author_email="",
    description="Decode FreeCAD's cryptic Topological Naming Problem (TNP) error messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/freecad-tnp-decoder",
    packages=find_packages(),
    package_data={
        'tnp_decoder': [
            'tools/__init__.py',
        ],
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: CAD",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    keywords="freecad tnp topological-naming parametric-modeling cad",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/freecad-tnp-decoder/issues",
        "Source": "https://github.com/yourusername/freecad-tnp-decoder",
        "FreeCAD": "https://www.freecadweb.org",
    },
)
