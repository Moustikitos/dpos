# -*- coding: utf-8 -*-

"""
`dposlib` is a package that provides simple and unique API to interact with Ark
blockchain and its forks.
"""

import os
import sys


# dposlib can be embeded in a frozen app
FROZEN = \
    hasattr(sys, "frozen") or hasattr(sys, "importers") \
    or ".egg" in __path__ or ".whl" in __path__

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
