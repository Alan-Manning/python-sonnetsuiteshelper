#!/usr/bin/env python
import re
from pathlib import Path

from setuptools import find_packages, setup


def read(*names, **kwargs):
    with Path(__file__).parent.joinpath(*names).open(encoding=kwargs.get("encoding", "utf8")) as fh:
        return fh.read()


setup(
    name="sonnetsuiteshelper",
    version="0.4.5",
    license="LGPL-3.0-or-later",
    description="A package to help with Sonnet Suites.",
    long_description="{}\n{}".format(
        re.compile("^.. start-badges.*^.. end-badges", re.M | re.S).sub("", read("README.rst")),
        re.sub(":[a-z]+:`~?(.*?)`", r"``\1``", read("CHANGELOG.rst")),
    ),
    author="Alan Manning",
    author_email="Alan_Manning@Live.co.uk",
    url="https://github.com/Alan-Manning/python-sonnetsuiteshelper",
    packages=find_packages("src"),
    package_dir={"": "src"},
    py_modules=[path.stem for path in Path("src").glob("*.py")],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
    ],
    project_urls={
        "Documentation": "https://python-sonnetsuiteshelper.readthedocs.io/",
        "Changelog": "https://python-sonnetsuiteshelper.readthedocs.io/en/latest/changelog.html",
        "Issue Tracker": "https://github.com/Alan-Manning/python-sonnetsuiteshelper/issues",
    },
    keywords=[
        "sonnet",
        "sonnetsuites",
        ".son",
    ],
    python_requires=">=3.10",
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "pyyaml",
    ],
    extras_require={},
    entry_points={
        "console_scripts": [
            "sonnetsuiteshelper = sonnetsuiteshelper.cli:main",
        ]
    },
)
