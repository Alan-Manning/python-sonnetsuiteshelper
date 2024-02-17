========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |github-actions|
        | |codecov|
    * - package
      - | |wheel| |supported-versions| |supported-implementations|
        | |commits-since|
.. |docs| image:: https://readthedocs.org/projects/python-sonnetsuiteshelper/badge/?style=flat
    :target: https://python-sonnetsuiteshelper.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/Alan-Manning/python-sonnetsuiteshelper/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/Alan-Manning/python-sonnetsuiteshelper/actions

.. |codecov| image:: https://codecov.io/gh/Alan-Manning/python-sonnetsuiteshelper/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/Alan-Manning/python-sonnetsuiteshelper

.. |wheel| image:: https://img.shields.io/pypi/wheel/sonnetsuiteshelper.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/sonnetsuiteshelper

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/sonnetsuiteshelper.svg
    :alt: Supported versions
    :target: https://pypi.org/project/sonnetsuiteshelper

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/sonnetsuiteshelper.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/sonnetsuiteshelper

.. |commits-since| image:: https://img.shields.io/github/commits-since/Alan-Manning/python-sonnetsuiteshelper/v0.4.5.svg
    :alt: Commits since latest release
    :target: https://github.com/Alan-Manning/python-sonnetsuiteshelper/compare/v0.4.5...main



.. end-badges

sonnetsuiteshelper is a package designed to help with editing and analysing `Sonnet Suites <https://www.sonnetsoftware.com/products/sonnet-suites/>`_ files.

* Free software: GNU Lesser General Public License v3 or later (LGPLv3+)

Installation
============

::

    pip install sonnetsuiteshelper

You can also install the in-development version with::

    pip install https://github.com/Alan-Manning/python-sonnetsuiteshelper/archive/main.zip


Documentation
=============


https://python-sonnetsuiteshelper.readthedocs.io/


Feature Requests
================


To request a new feature or extend existing features please create a github issue with the label "Feature Request"

https://github.com/Alan-Manning/python-sonnetsuiteshelper/issues


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
