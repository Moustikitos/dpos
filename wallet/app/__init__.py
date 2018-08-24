# -*- coding:utf-8 -*-

"""
(C) Toons MIT Licence
moustikitos@gmail.com

This package aims to provide a light wallet compatible with all ARK and LISK 
forks.

It relies on Flask, JS and CSS.
The app launches a wallet service available on `http://localhost:5000`
"""
import sys

PY3 = True if sys.version_info[0] >= 3 else False
from .app import app
