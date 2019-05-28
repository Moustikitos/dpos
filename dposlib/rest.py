# -*- coding: utf-8 -*-
# © Toons

"""
`rest` module loads networks constants to `cfg` module and provides endpoints
classes.

>>> from dposlib import rest
>>> rest.use("ark")
>>> # = 'https://explorer.ark.io:8443/api/delegates/arky'
>>> rest.GET.api.delegates.arky(peer="https://explorer.ark.io:8443")
{'data': {'username': 'arky', 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE', \
'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d60a15e\
9', 'votes': 149574938227265, 'rank': 26, 'blocks': {'produced': 163747, 'last'\
: {'id': '2824b47ba98d4af6dce4c8d548003d2da237777f8aee5cf905142b29138fe44f', 'h\
eight': 8482466, 'timestamp': {'epoch': 68943952, 'unix': 1559045152, 'human': \
'2019-05-28T12:05:52.000Z'}}}, 'production': {'approval': 1.19}, 'forged': {'fe\
es': 390146323536, 'rewards': 32465000000000, 'total': 32855146323536}}}
>>> rest.GET.api.delegates.arky() # in blockchain connection, peer is not mandatory
{'data': {'username': 'arky', 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE', \
'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d60a15e\
9', 'votes': 149574938227265, 'rank': 26, 'blocks': {'produced': 163747, 'last'\
: {'id': '2824b47ba98d4af6dce4c8d548003d2da237777f8aee5cf905142b29138fe44f', 'h\
eight': 8482466, 'timestamp': {'epoch': 68943952, 'unix': 1559045152, 'human': \
'2019-05-28T12:05:52.000Z'}}}, 'production': {'approval': 1.19}, 'forged': {'fe\
es': 390146323536, 'rewards': 32465000000000, 'total': 32855146323536}}}

`rest` also creates a `core` module into `dposlib` package containing
transactions functions and `crypto` module. 

>>> import dposlib
>>> dposlib.core.crypto.getKeys("secret")
{'publicKey': '03a02b9d5fdd1307c2ee4652ba54d492d1fd11a7d1bb3f3a44c4a05e79f19de9\
33', 'privateKey': '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf52\
7a25b', 'wif': 'SB3BGPGRh1SRuQd52h7f5jsHUg1G9ATEvSeA7L5Bz4qySQww4k7N'}
"""


import io
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
from dposlib import FROZEN, ROOT
from dposlib.blockchain import cfg
from dposlib.util.data import filter_dic


logging.getLogger("requests").setLevel(logging.CRITICAL)


def check_latency(peer):
	"""
	Returns latency in second for a given peer
	"""

	try:
		request = requests.get(peer, timeout=cfg.timeout, verify=cfg.verify)
	except Exception:
		# we want to capture all exceptions because we don't want to stop checking latency for
		# other peers that might be working
		return False
	return request.elapsed.total_seconds()


#################
#  API wrapper  #
#################

class EndPoint(object):

	@staticmethod
	def _manage_response(req, returnKey, error=None):
		# print(req.url)
		if req.status_code < 300:
			try:
				data = req.json()
			except Exception as error:
				data = {"success": True, "except": True, "data": req.text, "error": "%r"%error}
			else:
				tmp = data.get(returnKey, False)
				if not tmp:
					if returnKey:
						data["warning"] = "returnKey %s not found" % returnKey
				else:
					data = tmp
					if isinstance(tmp, dict):
						data = filter_dic(tmp)
			return data
		else:
			return {"success": False, "except": True, "error": "status code %s returned" % req.status_code}

	@staticmethod
	def _GET(*args, **kwargs):
		# API response contains several fields. Wanted one can be extracted using
		# a returnKey that match the field name
		return_key = kwargs.pop('returnKey', False)
		peer = kwargs.pop('peer', False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			req = requests.get(
				peer + "/".join(args),
				params=dict([k.replace('and_', 'AND:'), v] for k,v in kwargs.items()),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			)
		except Exception as error:
			return {"success": False, "error": "%r"%error, "except": True}
		else:
			return EndPoint._manage_response(req, return_key)

	@staticmethod
	def _POST(*args, **kwargs):
		return_key = kwargs.pop('returnKey', False)
		peer = kwargs.pop("peer", False)
		headers = kwargs.pop("headers", cfg.headers)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			req = requests.post(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			)
		except Exception as error:
			return {"success": False, "error": "%r"%error, "except": True}
		else:
			return EndPoint._manage_response(req, return_key)

	@staticmethod
	def _PUT(*args, **kwargs):
		return_key = kwargs.pop('returnKey', False)
		peer = kwargs.pop("peer", False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			req = requests.put(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			)
		except Exception as error:
			return {"success": False, "error": "%r"%error, "except": True}
		else:
			return EndPoint._manage_response(req, return_key)

	@staticmethod
	def _DELETE(*args, **kwargs):
		return_key = kwargs.pop('returnKey', False)
		peer = kwargs.pop("peer", False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			req = requests.delete(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			)
		except Exception as error:
			return {"success": False, "error": "%r"%error, "except": True}
		else:
			return EndPoint._manage_response(req, return_key)

	def __init__(self, elem=None, parent=None, method=None):
		if method not in [EndPoint._GET, EndPoint._POST, EndPoint._PUT, EndPoint._DELETE]:
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
		return (self.parent.chain() + [self.elem]) if self.parent!=None else [""]

GET = EndPoint(method=EndPoint._GET)
POST = EndPoint(method=EndPoint._POST)
PUT = EndPoint(method=EndPoint._PUT)
DELETE = EndPoint(method=EndPoint._DELETE)


#######################
#  network selection  #
#######################

def load(family_name):
	"""
	Loads a given blockchain package as `dposlib.core` module.
	"""

	if hasattr(sys.modules[__package__], "core"):
		try:
			sys.modules[__package__].core.stop()
		except Exception as e:
			sys.stdout.write("%r\n" % e)
		del sys.modules[__package__].core

	# initialize blockchain familly package
	try:
		sys.modules[__package__].core = import_module('dposlib.{0}'.format(family_name))
		sys.modules[__package__].core.init()
	except Exception as e:
		sys.stdout.write("%r\n" % e)
		raise Exception("%s is in readonly mode (no crypto package found)" % family_name)

	# delete real package name loaded to keep namespace clear
	try:
		sys.modules[__package__].__delattr__(family_name)
	except AttributeError:
		pass


def use(network, **kwargs):
	"""
	Sets the blockchain parameters in the `cfg` module and initialize blockchain
	package.
	"""

	# clear data in cfg module and initialize with minimum vars
	[cfg.__dict__.pop(k) for k in list(cfg.__dict__) if not k.startswith("_")]
	cfg.verify = os.path.join(os.path.dirname(sys.executable), 'cacert.pem') if FROZEN else True
	cfg.timeout = 5
	cfg.network = None
	cfg.hotmode = False
	cfg.broadcast = 10
	cfg.compressed = True
	cfg.minversion = "1.0"
	cfg.begintime = datetime.datetime(1970, 1, 1, tzinfo=pytz.UTC)
	cfg.headers = {"Content-Type": "application/json; charset=utf-8"}

	# try to load network.net configuration
	path = os.path.join(ROOT, "network", network + ".net")
	if os.path.exists(path):
		with io.open(os.path.join(ROOT, "network", network + ".net"), encoding='utf8') as f:
			data = json.load(f)
	else:
		raise Exception('"{}" blockchain parameters does not exist'.format(network))
	
	# override some options if given
	data.update(**kwargs)

	# connect with network to create peer nodes
	# seed is a complete url
	cfg.peers = []
	if data.get("seeds", False):
		for seed in data["seeds"]:
			if check_latency(seed):
				cfg.peers.append(seed)
				break

	if not len(cfg.peers):
		for peer in data.get("peers", []):
			peer = "http://{0}:{1}".format(peer, data.get("port", 22))
			if check_latency(peer):
				cfg.peers = [peer]
				break

	if len(cfg.peers):
		data.pop("peers", [])
		data.pop("seeds", [])
		# store options in cfg module
		cfg.__dict__.update(data)
		load(cfg.familly)
		cfg.network = network
		cfg.hotmode = True
	else:
		raise Exception("Error occurred during network setting...")
	
	return True
