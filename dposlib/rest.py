# -*- coding: utf-8 -*-
# © Toons

"""
`rest` module provides network loaders and `usrv.get.EndPoint` root class to
implement `GET`, `POST`, `PUT` and `DELETE` HTTP requests. See
[Ark API documentation](
    https://api.ark.dev/public-rest-api/getting-started
) to see how to use http calls.

`rest` also creates a `core` module containing
`dposlib.blockchain.tx.Transaction` builders, `dposlib.ark.crypto`
and `dposlib.ark.v2.api` interface.

## `rest` HTTP request builder
```python
>>> from dposlib import rest
>>> rest.use("ark")
True
>>> # reach http://api.ark.io/api/delegates/arky endpoint using GET
>>> # HTTP request builder
>>> rest.GET.api.delegates.arky()["username"]
'arky'
```

## `core` module
```python
>>> import dposlib
>>> dlgt = dposlib.core.api.Delegate("arky")
>>> dlgt.forged
{u'rewards': 397594.0, u'total': 401908.71166083, u'fees': 4314.71166083}
>>> dposlib.core.crypto.getKeys("secret")["publicKey"]
'03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de933'
>>> dposlib.core.transfer(
...     1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
...     u"\u2728 simple transfer vendorField"
... )
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 0,
  "vendorField": "\u2728 simple transfer vendorField",
  "version": 1
}
>>> dposlib.core.htlcLock(
...     1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
...     "my secret lock", expiration=12,
...     vendorField=u"\u2728 simple htlcLock vendorField"
... )
{
  "amount": 100000000,
  "asset": {
    "lock": {
      "secretHash":
        "dbaed2f2747c7aa5a834b082ccb2b648648758a98d1a415b2ed9a22fd29d47cb",
      "expiration": {
        "type": 1,
        "value": 82567745
      }
    }
  },
  "network": 23,
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 8,
  "typeGroup": 1,
  "vendorField": "\u2728 simple htlcLock vendorField",
  "version": 2
}
```
"""

import sys
import random
import datetime

import pytz

from importlib import import_module
from usrv import req
from dposlib import net
from dposlib.blockchain import cfg
from dposlib.util.data import filter_dic


def _call(method="GET", *args, **kwargs):
    returnKey = kwargs.pop("returnKey", False)
    response = req.EndPoint._open(
        req.EndPoint.build_req(method, *args, **kwargs)
    )
    if returnKey and returnKey in response:
        return filter_dic(response[returnKey])
    else:
        return response


def _random_peer(kwargs):
    return kwargs.pop("peer", None) or random.choice(cfg.peers)


#: GET HTTP request builder
GET = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("GET", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)
#: POST HTTP request builder
POST = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("POST", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)
#: PUT HTTP request builder
PUT = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("PUT", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)
#: DELETE HTTP request builder
DELETE = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("DELETE", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)


def load(name):
    """
    Load a given blockchain package as `dposlib.core` module. A valid
    blockchain package must provide `init(peer=None)` and `stop()` definitions.
    Available blockchains are referenced in `dposli.net` module.

    Arguments:
        name (str): package name to load
    """

    if hasattr(sys.modules[__package__], "core"):
        try:
            sys.modules[__package__].core.stop()
        except Exception as e:
            sys.stdout.write("%r\n" % e)
        del sys.modules[__package__].core
    # initialize blockchain familly package
    try:
        sys.modules[__package__].core = import_module(
            'dposlib.{0}'.format(name)
        )
    except ImportError as e:
        raise Exception("%s package not found\n%r" % (name, e))
    else:
        # delete real package name loaded to keep namespace clear
        try:
            sys.modules[__package__].__delattr__(name)
        except AttributeError:
            pass
        try:
            sys.modules[__package__].core.init()
        except Exception as e:
            raise Exception("package initialization error\n%r" % e)


def use(network, **kwargs):
    """
    Sets the blockchain parameters in the `dposlib.rest.cfg` module and
    initializes blockchain package. Network options can be created or overriden
    using `**kwargs` argument.

    Arguments:
        network (str): network to initialize
    Returns:
        True if network connection established
    """
    # clear data in cfg module
    [cfg.__dict__.pop(k) for k in list(cfg.__dict__) if not k.startswith("_")]
    # initialize minimum values
    cfg.begintime = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)
    cfg.headers = {
        "Content-Type": "application/json",
        "User-Agent": "Python/dposlib"
    }
    cfg.broadcast = 10     # maximum peer to use
    cfg.timeout = 5        # global timeout used within requests calls
    cfg.hotmode = False    # offline mode set
    cfg.network = network  # network name set
    cfg.peers = []         # peer list
    cfg.txversion = 1
    # load network.net configuration
    data = dict(getattr(net, network))
    # override some options if given
    data.update(**kwargs)
    # connect with first available seed
    for seed in data.pop("seeds", []):
        if req.connect(seed):
            cfg.peers.append(seed)
            cfg.hotmode = True
            break
    # update information on cfg module
    cfg.__dict__.update(data)
    load(cfg.familly)
    return cfg.hotmode
