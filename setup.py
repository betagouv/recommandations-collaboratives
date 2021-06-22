# coding: utf-8

"""
Setup for urbavitaliz-django deployment

For sdist deployments, do not forget MANIFEST.in file to include all the data files.
"""

from setuptools import setup
from setuptools import find_packages

import urbanvitaliz

setup(
    name="urbanvitaliz-django",
    version=urbanvitaliz.VERSION,
    description="Urbavitaliz application -django version",
    packages=find_packages(),
    include_package_data=True,
    author="Urbanvitaliz",
    author_email="urbanvitaliz@beta.gouv.fr",
    url="http://www.urbanvitaliz.fr",
)

# eof
