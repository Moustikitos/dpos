# -*- coding:utf-8 -*-
# created by Toons on 01/05/2017
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("VERSION") as f1, open("README.md") as f2:
    VERSION = f1.read().strip()
    LONG_DESCRIPTION = f2.read()

kw = {
    "version": VERSION,
    "name": "dposlib",
    "keywords": ["api", "ark", "blockchain"],
    "author": "Toons",
    "author_email": "moustikitos@gmail.com",
    "maintainer": "Toons",
    "maintainer_email": "moustikitos@gmail.com",
    "url": "https://github.com/Moustikitos/dpos",
    "download_url": "https://github.com/Moustikitos/dpos/archive/master.zip",
    "include_package_data": True,
    "description": "light api compatible with ARK blockchain and forks",
    "long_description": LONG_DESCRIPTION,
    "long_description_content_type": "text/markdown",
    "packages": [
        "dposlib",
        "dposlib.util",
        "dposlib.ark",
        "dposlib.ark.secp256k1",
        "dposlib.ark.v2",
        "dposlib.ark.v2.cold",
        "dposlib.blockchain",
    ],
    "install_requires": [
        "future",
        "pytz",
        "base58",
    ],
    "license": "Copyright 2018, MIT licence",
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
}

setup(**kw)
