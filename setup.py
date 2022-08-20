#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

readme = open('README.rst').read()
history = open('CHANGES.rst').read().replace('.. :changelog:', '')

setup(
    name="pyvalve",
    version='0.1.2',
    author="bsacks99",
    keywords = "python, asyncio, clamav, antivirus, scanner, virus, libclamav, clamd",
    description = "Asyncio python clamd client",
    long_description=readme + '\n\n' + history,
    url="https://github.com/bradsacks99/pyvalve",
    readme="README.md",
    license="LICENSE"
    package_dir={'': 'src'},
    packages=find_packages('src', exclude="tests"),
    classifiers = [
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    ],
    zip_safe=True,
    include_package_data=False,
)