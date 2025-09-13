#!/usr/bin/env python3
"""Setup script for Phoenix - AI-Powered C++ Documentation Suite."""

from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Read requirements
requirements = []
with open("requirements.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            # Remove version constraints for setup.py (optional)
            requirements.append(line.split(">=")[0])

setup(
    name="phoenix-cpp-docs",
    version="1.0.0",
    description="AI-Powered C++ Documentation Suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/phoenix",
    author="Pranay + AI",
    author_email="your-email@example.com",
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Operating System :: OS Independent",
    ],
    keywords="documentation, c++, ai, automation, doxygen, tree-sitter, ollama",
    packages=find_packages(),
    python_requires=">=3.8, <4",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.9.0",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.1.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "phoenix-gui=phoenix.auto_comment_cpp_code:main",
            "phoenix-extract=phoenix.extract_function_code_2:main",
            "phoenix-git=phoenix.get_git_changes:main",
            "phoenix-docs=phoenix.generate_docs_ollama:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/your-username/phoenix/issues",
        "Source": "https://github.com/your-username/phoenix/",
        "Documentation": "https://github.com/your-username/phoenix/wiki",
    },
    package_data={
        "phoenix": [
            "config/*.json",
            "examples/*.py",
            "assets/*",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)