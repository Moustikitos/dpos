# -*- coding: utf-8 -*-
# © Toons

"""
:mod:`rest` module provides network loaders and root
:class:`EndPoint` ``GET``, ``POST``, ``PUT`` and ``DELETE``. See
`Ark API documentation <https://api.ark.dev/public-rest-api/getting-started>`_
to see how to use http calls.

:mod:`rest` also creates a `core <core.html>`_ module containing
:class:`Transaction` builders, :mod:`crypto` and :mod:`api` modules.

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
import datetime

import pytz

from importlib import import_module
from dposlib import FROZEN, PY3, net
from dposlib.blockchain import cfg
from dposlib.util.data import filter_dic

if PY3:
    from urllib.request import Request, OpenerDirector, HTTPHandler
    from urllib.request import HTTPSHandler, BaseHandler
    from urllib.parse import urlencode
else:
    from urllib2 import Request, OpenerDirector, HTTPHandler, HTTPSHandler
    from urllib2 import BaseHandler
    from urllib import urlencode


#################
#  API wrapper  #
#################

class EndPoint(object):
    """
    This class is at the root of interaction with Ark JSON API. Build the
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
    opener = None

    def __init__(self, elem=None, parent=None, method=lambda: None):
        self.elem = elem
        self.parent = parent
        self.method = method

        if EndPoint.opener is None:
            EndPoint.opener = OpenerDirector()
            for handler in [HTTPHandler, HTTPSHandler]:
                EndPoint.opener.add_handler(handler())

    def add_handler(self, handler):
        if not isinstance(handler, BaseHandler):
            raise Exception(
                "%r have to be a %r instance" % (handler, BaseHandler)
            )
        if not isinstance(EndPoint.opener, OpenerDirector):
            EndPoint.opener = OpenerDirector()
        EndPoint.opener.add_handler(handler)

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

    @staticmethod
    def _call(method="GET", *args, **kwargs):
        method = method.upper()
        peer = kwargs.pop("peer", False)
        return_key = kwargs.pop('returnKey', False)
        headers = kwargs.pop("headers", dict(cfg.headers))
        to_urlencode = kwargs.pop("urlencode", None)
        to_jsonify = kwargs.pop("jsonify", None)
        # build request
        url = \
            (peer if bool(peer) else random.choice(cfg.peers)) + "/".join(args)
        if method == "GET":
            if len(kwargs):
                url += "?" + urlencode(
                    dict(
                        [
                            (k.replace('and_', 'AND:'), v)
                            for k, v in kwargs.items()
                        ]
                    )
                )
            req = Request(url, None, headers)
        else:
            if to_urlencode != to_jsonify:
                if len(kwargs):
                    url += "?" + urlencode(
                        dict(
                            [
                                (k.replace('and_', 'AND:'), v)
                                for k, v in kwargs.items()
                            ]
                        )
                    )
            headers["Content-type"] = "application/json"
            if to_urlencode is not None:
                data = urlencode(to_urlencode)
                headers["Content-type"] = "application/x-www-form-urlencoded"
            elif to_jsonify is not None:
                data = json.dumps(to_jsonify)
            elif len(kwargs):
                data = json.dumps(kwargs)
            else:
                data = json.dumps({})
            req = Request(url, data.encode('utf-8'), headers)
        # tweak request
        req.add_header("User-agent", "Mozilla/5.0")
        req.get_method = lambda: method
        # send request
        try:
            res = EndPoint.opener.open(req, timeout=cfg.timeout)
        except Exception as error:
            return {"success": False, "error": "%r" % error, "except": True}
        else:
            return EndPoint._manage_response(res, return_key)

    @staticmethod
    def _manage_response(res, returnKey, error=None):
        # first try to jsonify response
        text = res.read()
        try:
            data = json.loads(text)
        except Exception as err:
            data = {
                "success": True, "except": True,
                "raw": text, "error": "%r" % err
            }

        if res.getcode() < 300 and returnKey:
            # else try to extract the returnKey
            tmp = data.get(returnKey, False)
            if not tmp:
                data["warning"] = "returnKey %s not found" % returnKey
            # filter the result if returnKey gives a dict instance
            else:
                data = tmp
                if isinstance(tmp, dict):
                    data = filter_dic(tmp)
                elif isinstance(tmp, list):
                    data = [filter_dic(e) for e in data]

        return data


GET = EndPoint(method=lambda *a, **kw: EndPoint._call("GET", *a, **kw))
POST = EndPoint(method=lambda *a, **kw: EndPoint._call("POST", *a, **kw))
PUT = EndPoint(method=lambda *a, **kw: EndPoint._call("PUT", *a, **kw))
DELETE = EndPoint(method=lambda *a, **kw: EndPoint._call("DELETE", *a, **kw))


#######################
#  network selection  #
#######################

def isOnline(peer):
    try:
        response = EndPoint.opener.open(peer, timeout=cfg.timeout)
    except Exception:
        response = False
    return True if response else False


def load(name):
    """
    Load a given blockchain package as ``dposlib.core`` module. A valid
    blockchain package must provide :func:`init(peer=None)` and :func:`stop()`
    definitions. Available blockchains are referenced in :mod:`dposli.net`
    module.

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

    Returns:
        :class:`bool`: True if network connection established
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
    cfg.txversion = 1

    # load network.net configuration
    data = dict(getattr(net, network))
    # override some options if given
    data.update(**kwargs)

    # connect with first available seed
    for seed in data.pop("seeds", []):
        if isOnline(seed):
            cfg.peers.append(seed)
            cfg.hotmode = True
            break

    cfg.__dict__.update(data)
    load(cfg.familly)

    return cfg.hotmode
