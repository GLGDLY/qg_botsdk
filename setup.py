# !/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qg-botsdk",
    version="2.5.3",
    author="GDLY",
    author_email="tzlgdly@gmail.com",
    description="easy-to-use SDK for Tencent QQ guild robot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GLGDLY/qg_botsdk",
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp>=3.8.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools"
    ],
    python_requires='>=3.7',
)
