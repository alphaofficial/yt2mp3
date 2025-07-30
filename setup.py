#!/usr/bin/env python3

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="yt2mp3",
    version="1.0.0",
    author="yt2mp3",
    description="YouTube to MP3 Converter - Download YouTube videos and convert them to MP3 format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/yt2mp3",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.7",
    install_requires=[
        "yt-dlp>=2023.12.30",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "yt2mp3=yt2mp3:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)