# -*- coding: utf-8 -*-

"""
Cardano specific package trough [`Blockfrost`](https://blockfrost.io) provider.

You have to signup first and create a project. Token can be used on cardano
testnet `shelley` or mainnet `ada` according to your project. `blockfrost` API
can be requested using `rest` module.

```python
>>> from dposlib import rest
>>> rest.use("shelley")
Paste your blockfrost.io token > testn...YceJXT
True
>>> rest.GET.blocks.latest()
{
    'time': 1637339033,
    'height': 3086136,
    'hash': '72cd383b6c6c5a1a1027b11da58b637eb60ab1520247da10f1558ce2544cb129',
    'slot': 42969817,
    'epoch': 169,
    'epoch_slot': 331417,
    'slot_leader': 'pool1ta0df6et5d22k2khezze70dvly6kgcm6zp0gpjxc5lwrce0seyq',
    'size': 630,
    'tx_count': 2,
    'output': '49900070463',
    'fees': '339142',
    'block_vrf':
        'vrf_vk1rm9kkh9czf6v2a2qe5ah3jzrh4gr8y04ezsjak79wkspfnn4e73qfdxp5n',
    'previous_block':
        'fa98d456b0be6ac38f86222f3606d122e4b2d9216280fd861c06a3b08caeb078',
    'next_block': None,
    'confirmations': 0,
    'status': 200
}
```

[Available endpoints](https://docs.blockfrost.io)
"""

import os
import sys

from dposlib import cfg, rest, ROOT
from dposlib.util import data


def init(seed=None):
    token = None
    json_file = os.path.join(ROOT, ".json", "blockfrost.token")
    tokens = data.loadJson(json_file)

    available = [t for t in tokens if tokens[t] == rest.cfg.network]
    if available:
        try:
            sys.stdout.write("Available token [0=last]:\n")
            for t in available:
                sys.stdout.write(" - %d : %s\n" % (available.index(t)+1, t))
            token = available[int(input("Select token number > "))-1]
        except Exception:
            pass
        else:
            sys.stdout.write("Blockfrost account: %s\n" % token)

    if not token:
        token = input("Paste your blockfrost.io token > ")

    cfg.headers["project_id"] = token

    check = rest.GET.health.clock().get("status", False) == 200
    if check:
        tokens[token] = rest.cfg.network
        data.dumpJson(tokens, json_file)

    return check


def stop():
    pass


__all__ = []
