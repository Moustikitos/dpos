# -*- coding: utf-8 -*-
# © Toons

"""
# dposlib

`dposlib` is a package that provides REST API and to interact with ARK
blockchain and its forks. It is designed to run with both python 2.x and 3.x.

```python
>>> import dposlib
>>> from dposlib import rest
>>> rest.use("ark")
True
>>> delegate0 = rest.GET.api.delegates(returnKey="data")[0]
>>> delegate0["username"]
u'binance_staking'
```
"""

import os
import sys

PY3 = sys.version_info[0] >= 3

if PY3:
    import io
    BytesIO = io.BytesIO
else:
    from cStringIO import StringIO
    BytesIO = StringIO


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
