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
	"keywords": ["cli", "wallet", "dpos", "blockchain"],
	"author": "Toons",
	"author_email": "moustikitos@gmail.com",
	"maintainer": "Toons",
	"maintainer_email": "moustikitos@gmail.com",
	"url": "https://github.com/Moustikitos/dpos",
	"download_url": "https://github.com/Moustikitos/dpos/archive/master.zip",
	"include_package_data": True,
	"description": "light wallet compatible with all ARK and LISK forks",
	"long_description": LONG_DESCRIPTION,
	"packages": [
		"dposlib.util",
		"dposlib.wallet",
		"dposlib.wallet.app",
		"dposlib.ark",
		"dposlib.blockchain"
	],
	"install_requires": [
		"requests",
		"ecdsa",
		"pynacl",
		"pytz",
		"base58",
		# "ledgerblue",
		"flask"
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
