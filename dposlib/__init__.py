# -*- coding: utf-8 -*-
# © Toons

"""
`dposlib` is a package providing REST API and to interact with ark and ark
forks.

It is designed to run with both python 2.x and 3.x.
"""

import os
import sys
# import imp


PY3 = True if sys.version_info[0] >= 3 else False

if PY3:
    import io
    BytesIO = io.BytesIO
else:
    from cStringIO import StringIO
    BytesIO = StringIO

# dposlib can be embeded in a frozen app
FROZEN = \
    hasattr(sys, "frozen") or hasattr(sys, "importers")
    #  or \
    # imp.is_frozen("__main__")

if FROZEN:
    # if frozen code, HOME and ROOT pathes are same
    HOME = ROOT = os.path.normpath(
        os.path.abspath(os.path.dirname(sys.executable))
    )
else:
    ROOT = os.path.normpath(os.path.abspath(os.path.dirname(__file__)))
    # deal the HOME directory according to OS
    try:
        HOME = os.path.join(os.environ["HOMEDRIVE"], os.environ["HOMEPATH"])
    except Exception:
        HOME = os.environ.get("HOME", ROOT)
    finally:
        HOME = os.path.normpath(HOME)

if HOME not in sys.path:
    sys.path.append(HOME)
