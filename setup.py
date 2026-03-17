# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in posawesome/__init__.py
# from posawesome import __version__ as version
with open("posawesome/__init__.py", "r", encoding="utf-8") as f:
    version = re.search(
        r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]',
        f.read()
    ).group(1)

setup(
    name="posawesome",
    version=version,
    description="POS Awesome",
    author="Yousef Restom",
    author_email="youssef@totrox.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
