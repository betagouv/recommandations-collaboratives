# coding: utf-8

"""
Setup for recoco deployment

For sdist deployments, do not forget MANIFEST.in file to include all the data files.
"""

from setuptools import find_packages, setup

import recoco

setup(
    name="recoco",
    version=recoco.VERSION,
    description="Recoconseil application",
    packages=find_packages(),
    include_package_data=True,
    author="Recoconseil Dev Team",
    author_email="recoco@beta.gouv.fr",
    url="http://www.recoconseil.fr",
)

# eof
