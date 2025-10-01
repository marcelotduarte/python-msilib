# python-msilib

Read and write Microsoft Installer files.

This library is legacy code borrowed from Python 3.12, intended to allow
cx_Freeze's bdist_msi command to continue working in Python 3.13 and 3.14.

[![PyPI version](https://img.shields.io/pypi/v/python-msilib)](https://pypi.org/project/python-msilib/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/python-msilib)](https://pypistats.org/packages/python-msilib)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/python-msilib.svg)](https://anaconda.org/conda-forge/python-msilib)
[![Conda Downloads](https://anaconda.org/conda-forge/python-msilib/badges/downloads.svg)](https://anaconda.org/conda-forge/python-msilib)
[![Python](https://img.shields.io/pypi/pyversions/python-msilib)](https://www.python.org/)
[![Coverage](https://raw.githubusercontent.com/marcelotduarte/python-msilib/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/marcelotduarte/python-msilib/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Installation

Choose the Python package manager according to your system. See how the
installation works with the most common ones, which are pip and conda.

To install the latest version of `python-msilib` using `pip` into a
virtual environment:

```
pip install --upgrade python-msilib
```

To install the latest development build:

```
pip uninstall python-msilib
pip install --extra-index-url https://test.pypi.org/simple/ python-msilib --pre --no-cache
```

Installing python-msilib from the conda-forge channel can be achieved with the
command:

```
conda install conda-forge::python-msilib
```

## Documentation

Please read the documentation at Python
[docs](https://docs.python.org/3.12/library/msilib.html).
