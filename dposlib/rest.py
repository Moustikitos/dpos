# -*- coding: utf-8 -*-
# © Toons

"""
:mod:`rest` module cointains network loaders and provides root
:class:`EndPoint` ``GET``, ``POST``, ``PUT`` and ``DELETE``. See
`Ark API documentation <https://api.ark.dev/public-rest-api/getting-started>`_
to see how to use http calls.

:mod:`rest` also creates a `core <core.html>`_ module containing :mod:`crypto`
and :mod:`api` module plus :class:`Transaction` builders.

>>> from dposlib import rest
>>> rest.use("ark")
True
>>> import dposlib
>>> dlgt = dposlib.core.api.Delegate("arky")
>>> dlgt.forged
{u'rewards': 397594.0, u'total': 401908.71166083, u'fees': 4314.71166083}
>>> dposlib.core.crypto.getKeys("secret")
{'publicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de\
933', 'privateKey': '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf\
527a25b', 'wif': 'SB3BGPGRh1SRuQd52h7f5jsHUg1G9ATEvSeA7L5Bz4qySQww4k7N'}
>>> dposlib.core.transfer(1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE", u"\u2728 si\
mple transfer vendorField")
{
  "amount": 100000000,
  "asset": {},
  "recipientId": "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE",
  "type": 0,
  "vendorField": "\u2728 simple transfer vendorField",
  "version": 1
}
>>> dposlib.core.htlcLock(1, "ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE", "my secret \
lock", expiration=12, vendorField=u"\u2728 simple htlcLock vendorField")
{
  "amount": 100000000,
  "asset": {
    "lock": {
      "secretHash": "dbaed2f2747c7aa5a834b082ccb2b648648758a98d1a415b2ed9a22fd\
29d47cb",
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
"""

import os
import re
import sys
import json
import random
import logging
import datetime

import pytz
import requests

from importlib import import_module
from dposlib import FROZEN, net
from dposlib.blockchain import cfg
from dposlib.util.data import filter_dic

logging.getLogger("requests").setLevel(logging.CRITICAL)


def checkLatency(peer):
    """
    Returns latency in second for a given peer

    Args:
        peer (:class:`str`): the peer in the scheme http(s)://[ip]:[port]

    Returns:
        :class:`float`: latency in seconds
    """

    try:
        request = requests.get(peer, timeout=cfg.timeout, verify=cfg.verify)
    except Exception:
        # we want to capture all exceptions because we don't want to stop
        # checking latency for other peers that might be working
        return False
    return request.elapsed.total_seconds()


#################
#  API wrapper  #
#################

class EndPoint(object):
    """
    This class is at the root of interaction with http JSON API. Build the
    endpoint concatening multiple attributes, named accordingly to endpoint
    path, and call the last one.

    Equivalent to https://explorer.ark.io:8443/api/delegates/arky API call:

    >>> rest.GET.api.delegates.arky(peer="https://explorer.ark.io:8443")
    {'data': {'username': 'arky', 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88v\
WE', 'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d\
60a15e9', 'votes': 149574938227265, 'rank': 26, 'blocks': {'produced':163747, \
'last': {'id': '2824b47ba98d4af6dce4c8d548003d2da237777f8aee5cf905142b29138fe4\
4f', 'height': 8482466, 'timestamp': {'epoch': 68943952, 'unix': 1559045152, '\
human': '2019-05-28T12:05:52.000Z'}}}, 'production': {'approval': 1.19}, 'forg\
ed': {'fees': 390146323536, 'rewards': 32465000000000, 'total': 32855146323536\
}}}

    Within a blockchain connection, peer is not mandatory:

    >>> rest.GET.api.delegates.arky()
    {'data': {'username': 'arky', 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88v\
WE', 'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d\
60a15e9', 'votes': 149574938227265, 'rank': 26, 'blocks': {'produced':163747, \
'last': {'id': '2824b47ba98d4af6dce4c8d548003d2da237777f8aee5cf905142b29138fe4\
4f', 'height': 8482466, 'timestamp': {'epoch': 68943952, 'unix': 1559045152, '\
human': '2019-05-28T12:05:52.000Z'}}}, 'production': {'approval': 1.19}, 'forg\
ed': {'fees': 390146323536, 'rewards': 32465000000000, 'total': 32855146323536\
}}}
"""

    @staticmethod
    def _manage_response(req, returnKey, error=None):
        # first try to jsonify response
        try:
            data = req.json()
        except Exception as error:
            data = {
                "success": True, "except": True, "data": req.text,
                "error": "%r" % error
            }

        if req.status_code < 300:
            # else try to extract the returnKey
            tmp = data.get(returnKey, False)
            if not tmp:
                if returnKey:
                    data["warning"] = "returnKey %s not found" % returnKey
            # filter the result if returnKey gives a dict instance
            else:
                data = tmp
                if isinstance(tmp, dict):
                    data = filter_dic(tmp)
                elif isinstance(tmp, list):
                    data = [filter_dic(e) for e in data]

        return data

    @staticmethod
    def _GET(*args, **kwargs):
        # API response contains several fields. Wanted one can be extracted
        # using a returnKey that match the field name
        return_key = kwargs.pop('returnKey', False)
        peer = kwargs.pop('peer', False)
        peer = peer if bool(peer) else random.choice(cfg.peers)
        try:
            req = requests.get(
                peer + "/".join(args),
                params=dict(
                    [k.replace('and_', 'AND:'), v] for k, v in kwargs.items()
                ),
                headers=cfg.headers,
                verify=cfg.verify,
                timeout=cfg.timeout
            )
        except Exception as error:
            return {"success": False, "error": "%r" % error, "except": True}
        else:
            return EndPoint._manage_response(req, return_key)

    @staticmethod
    def _POST(*args, **kwargs):
        return_key = kwargs.pop('returnKey', False)
        peer = kwargs.pop("peer", False)
        headers = kwargs.pop("headers", cfg.headers)
        peer = peer if bool(peer) else random.choice(cfg.peers)
        try:
            req = requests.post(
                peer + "/".join(args),
                data=json.dumps(kwargs),
                headers=headers,
                verify=cfg.verify,
                timeout=cfg.timeout
            )
        except Exception as error:
            return {"success": False, "error": "%r" % error, "except": True}
        else:
            return EndPoint._manage_response(req, return_key)

    @staticmethod
    def _PUT(*args, **kwargs):
        return_key = kwargs.pop('returnKey', False)
        peer = kwargs.pop("peer", False)
        peer = peer if bool(peer) else random.choice(cfg.peers)
        try:
            req = requests.put(
                peer + "/".join(args),
                data=json.dumps(kwargs),
                headers=cfg.headers,
                verify=cfg.verify,
                timeout=cfg.timeout
            )
        except Exception as error:
            return {"success": False, "error": "%r" % error, "except": True}
        else:
            return EndPoint._manage_response(req, return_key)

    @staticmethod
    def _DELETE(*args, **kwargs):
        return_key = kwargs.pop('returnKey', False)
        peer = kwargs.pop("peer", False)
        peer = peer if bool(peer) else random.choice(cfg.peers)
        try:
            req = requests.delete(
                peer + "/".join(args),
                data=json.dumps(kwargs),
                headers=cfg.headers,
                verify=cfg.verify,
                timeout=cfg.timeout
            )
        except Exception as error:
            return {"success": False, "error": "%r" % error, "except": True}
        else:
            return EndPoint._manage_response(req, return_key)

    def __init__(self, elem=None, parent=None, method=None):
        if method not in [
            EndPoint._GET, EndPoint._POST, EndPoint._PUT, EndPoint._DELETE
        ]:
            raise Exception("REST method nort implemented")
        self.elem = elem
        self.parent = parent
        self.method = method

    def __getattr__(self, attr):
        if attr not in ["elem", "parent", "method", "chain"]:
            if re.match("^_[0-9A-Fa-f].*", attr):
                attr = attr[1:]
            return EndPoint(attr, self, self.method)
        else:
            return object.__getattr__(self, attr)

    def __call__(self, *args, **kwargs):
        return self.method(*self.chain()+list(args), **kwargs)

    def chain(self):
        return (self.parent.chain() + [self.elem]) if self.parent is not None \
               else [""]


GET = EndPoint(method=EndPoint._GET)
POST = EndPoint(method=EndPoint._POST)
PUT = EndPoint(method=EndPoint._PUT)
DELETE = EndPoint(method=EndPoint._DELETE)


#######################
#  network selection  #
#######################

def load(name):
    """
    Loads a given blockchain package as ``dposlib.core`` module. A valid
    blockchain package must provide ``init(peer=None)`` and ``stop()``
    definitions.

    Args:
        name (:class:`str`): package name to load
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
    Sets the blockchain parameters in the ``cfg`` module and initialize
    blockchain package. Network options can be created or overriden using
    ``**kwargs`` argument.

    Args:
        network (:class:`str`): network to initialize
    """

    # clear data in cfg module
    [cfg.__dict__.pop(k) for k in list(cfg.__dict__) if not k.startswith("_")]

    # initialize minimum values
    cfg.verify = \
        os.path.join(os.path.dirname(sys.executable), 'cacert.pem') if FROZEN \
        else True  # activate https for requests lib
    cfg.begintime = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)
    cfg.headers = {"Content-Type": "application/json"}
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
        if checkLatency(seed):
            cfg.peers.append(seed)
            cfg.hotmode = True
            break

    cfg.__dict__.update(data)
    load(cfg.familly)

    return cfg.hotmode
