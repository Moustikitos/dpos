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
	"name": "wallet",
	"keywords": ["lite", "wallet", "dpos", "blockchain"],
	"author": "Toons",
	"author_email": "moustikitos@gmail.com",
	"maintainer": "Toons",
	"maintainer_email": "moustikitos@gmail.com",
	"url": "https://github.com/Moustikitos/dpos",
	"download_url": "https://github.com/Moustikitos/dpos/archive/master.zip",
	"include_package_data": True,
	"description": "light wallet compatible with all ARK and LISK forks",
	"long_description": LONG_DESCRIPTION,
	"packages": ["wallet", "wallet.app"],
	"install_requires": ["arky>=1.4", "flask", "six"],
	"scripts": [
		"bin/wsgi.py"
	],
	"license": "Copyright 2018, MIT licence",
	"classifiers": [
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Environment :: Web Environment",
		"Framework :: Flask",
		"Intended Audience :: Developers",
		"Intended Audience :: End Users/Desktop",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Programming Language :: Python :: 2",
	],
}

setup(**kw)
