========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis| |appveyor| |requires|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/tsv2dict/badge/?style=flat
    :target: https://readthedocs.org/projects/tsv2dict
    :alt: Documentation Status

.. |travis| image:: https://api.travis-ci.com/nkurmann/tsv2dict.svg?branch=main
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/github/nkurmann/tsv2dict

.. |appveyor| image:: https://ci.appveyor.com/api/projects/status/github/nkurmann/tsv2dict?branch=main&svg=true
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/nkurmann/tsv2dict

.. |requires| image:: https://requires.io/github/nkurmann/tsv2dict/requirements.svg?branch=main
    :alt: Requirements Status
    :target: https://requires.io/github/nkurmann/tsv2dict/requirements/?branch=main

.. |codecov| image:: https://codecov.io/gh/nkurmann/tsv2dict/branch/master/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://codecov.io/github/nkurmann/tsv2dict

.. |version| image:: https://img.shields.io/pypi/v/tsv2dict.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/tsv2dict

.. |wheel| image:: https://img.shields.io/pypi/wheel/tsv2dict.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/tsv2dict

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/tsv2dict.svg
    :alt: Supported versions
    :target: https://pypi.org/project/tsv2dict

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/tsv2dict.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/tsv2dict

.. |commits-since| image:: https://img.shields.io/github/commits-since/nkurmann/tsv2dict/v0.0.3.svg
    :alt: Commits since latest release
    :target: https://github.com/nkurmann/tsv2dict/compare/v0.0.2...main



.. end-badges

Python support for linear TSV files

* Free software: MIT license


What is Linear TSV
==================

In contrast to Excel's TSV dialect, linear TSV is line-based.

*"But hey"*, I hear you say, *"isn't TSV always line-based?"*. Well, the issue arises when a cell contains a tab or newline character. In excel's TSV format, that cell is surrounded by quotes and the entry is continued on the next line. Now you have:

* entries spanning several lines
* quotes that need to be ignored (`"`)
* quotes that are escaped by doubling them (`""`)

Since entries can span several lines, many naïve file manipulations aren't possible:

* Taking the first 50 entries of a dataset: `head -n 50 customers.tsv`
* Filtering entries: `grep "Zürich" customers.tsv`
* Sorting the entries alphabetically: `sort customers.tsv`

All of this can be prevented if you simply:

* escape tabs: `\\t`
* escape newlines: `\\n`
* escape carriage returns: `\\r`
* escape backslashes: `\\\\`

Lastly, linear TSV can also encode `None` as `\\N`.

That's linear tsv in a nutshell.


Installation
============

::

    pip install tsv2dict

You can also install the in-development version with::

    pip install https://github.com/nkurmann/tsv2dict/archive/master.zip


Documentation
=============


https://tsv2dict.readthedocs.io/


Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
