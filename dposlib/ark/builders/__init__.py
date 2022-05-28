# -*- coding: utf-8 -*-
# © Toons


"""
[`dposlib.ark.builders`](builders.md#dposlib.ark.builders) package
provides[ `dposlib.ark.tx.Transaction`](tx.md#dposlib.ark.tx.Transaction)
class and its associated builders.

```python
>>> from dposlib import rest
>>> rest.use("dark")
True
>>> from dposlib.ark.v2 import *
>>> tx = transfer(
...   1,
...   "D7seWn8JLVwX4nHd9hh2Lf7gvZNiRJ7qLk",
...   u"simple message with sparkle \u2728",
...   version=2
... )
>>> tx.finalize("first secret", "second secret")
>>> broadcastTransactions(tx).get("data", {}).get("broadcast", [])
[u'041ad1e3dd06d29ef59b2c7e19fea4ced0e7fcf9fdc22edcf26e5cc016e10f38']
```
"""

from dposlib import rest, cfg

from . import v2, v3

CACHE = {}


def _getattr(mod, name):
    func = CACHE.get(name, False)
    if func is False:
        for version in range(cfg.txversion, 1, -1):
            sub_mod = getattr(mod, f"v{version}", None)
            if sub_mod is not None and hasattr(sub_mod, name):
                CACHE[name] = getattr(sub_mod, name)
                return CACHE[name]
        raise NotImplementedError()
    else:
        return func


def broadcastTransactions(*transactions, **params):
    chunk_size = params.pop("chunk_size", cfg.maxTransactions)
    report = []
    for chunk in [
        transactions[i:i+chunk_size] for i in
        range(0, len(transactions), chunk_size)
    ]:
        report.append(rest.POST.api.transactions(transactions=chunk))
    return \
        None if len(report) == 0 else \
        report[0] if len(report) == 1 else \
        report
