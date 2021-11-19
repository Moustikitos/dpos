# -*- coding: utf-8 -*-

"""
`rest` module provides network loaders and [`usrv.req.EndPoint`](
    https://github.com/Moustikitos/micro-server/blob/master/usrv/req.py#L38
) root class to implement `GET`, `POST`, `PUT` and `DELETE` HTTP requests.

When a specific blockchain package is loaded through `rest.use` definition, a
`dposlib.core` module is available to provide necessary classes and
definitions.
"""

import sys
import random
import datetime
import traceback
from importlib import import_module

import pytz
from usrv import req
from dposlib import net, cfg
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
    return kwargs.pop("peer", None) or (
        random.choice(cfg.peers) if len(cfg.peers) else None
    )


#: HTTP GET request builder
GET = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("GET", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)
#: HTTP POST request builder
POST = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("POST", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)
#: HTTP PUT request builder
PUT = req.EndPoint(
    method=lambda *a, **kw: [
        setattr(req.EndPoint, "peer", _random_peer(kw)),
        _call("PUT", *a, **dict(kw, headers=cfg.headers))
    ][-1]
)
#: HTTP DELETE request builder
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

    Args:
        name (str): package name to load.

    Raises:
        Exception: if package name is not found or if package can not be
            initialized properly.
    """
    if hasattr(sys.modules[__package__], "core"):
        try:
            sys.modules[__package__].core.stop()
        except Exception as e:
            sys.stdout.write("%r\n" % e)
        del sys.modules[__package__].core
    # initialize blockchain familly package
    try:
        sys.modules[__package__].core = import_module(f'dposlib.{name}')
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
        except Exception as error:
            raise Exception(
                "package initialization error\n%r\n%s" %
                (error, traceback.format_exc())
            )


def use(network, **kwargs):
    """
    Sets the blockchain parameters in the `dposlib.rest.cfg` module and
    initializes blockchain package. Network options can be created or overriden
    using `**kwargs` argument.

    Args:
        network (str): network to initialize.
        **kwargs: parameters to be overriden.

    Returns:
        bool: True if network connection established, False otherwise.

    Raises:
        Exception: if blockchain not defined or if initialization failed.
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
    req.EndPoint.timeout = cfg.timeout
    req.EndPoint.quiet = True
    load(cfg.familly)
    return cfg.hotmode
