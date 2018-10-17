# -*- coding: utf-8 -*-
# © Toons

"""
`dposlib` is a package providing REST API and a CLI  to interact with major dpos
blockchain environement.

It is designed to run on boh python 2.x and 3.x exept for the wallet wich
runs with python 2.x
"""

import os
import sys
import imp


PY3 = True if sys.version_info[0] >= 3 else False

if PY3:
	import io
	BytesIO = io.BytesIO
else:
	from cStringIO import StringIO as BytesIO

# dposlib can be embeded in a frozen app
FROZEN = hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__")

if FROZEN:
	# if frozen code, HOME and ROOT pathes are same
	HOME = ROOT = os.path.normpath(os.path.abspath(os.path.dirname(sys.executable)))
	LOGNAME = os.path.join(ROOT, __name__ + ".log")
else:
	ROOT = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
	# deal the HOME directory according to OS
	try:
		HOME = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
	except:
		HOME = os.environ.get("HOME", ROOT)
	LOGNAME = os.path.normpath(os.path.join(HOME, "." + __name__))
