"""
Setup script for Aureum Python package

Install with:
    pip install -e .

Or build wheel:
    python setup.py bdist_wheel

Author: Luiz Antonio De Lima Mendonca
Location: Resende, RJ, Brazil
Instagram: @luizinvict
Date: 2026-03-25
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="aureum",
    version="0.1.0",
    author="Luiz Antonio De Lima Mendonca",
    author_email="luizinvict@example.com",
    description="Ultra-fast AI library with 2-bit weights - 100x faster than NumPy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luizinvict/aureum",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Rust",
    ],
    python_requires=">=3.8",
    install_requires=[
        "lark>=1.1.0",
        "psutil>=5.9.0",
        "numpy>=1.20.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "aureum=main:main",
            "aureum-shell=shell:main",
        ],
    },
    include_package_data=True,
    package_data={
        "aureum": [
            "frontend/*.lark",
            "backend/target/release/*.so",
            "backend/target/release/*.dll",
            "backend/target/release/*.dylib",
        ],
    },
    keywords=[
        "ai",
        "machine-learning",
        "deep-learning",
        "bitnet",
        "quantization",
        "edge-ai",
        "numpy",
        "pytorch",
        "performance",
        "rust",
    ],
    project_urls={
        "Bug Reports": "https://github.com/luizinvict/aureum/issues",
        "Source": "https://github.com/luizinvict/aureum",
        "Documentation": "https://github.com/luizinvict/aureum/blob/main/README.md",
    },
)
