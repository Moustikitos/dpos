# -*- coding: utf-8 -*-
# © Toons

"""
`rest` module It loads networks constants to `cfg` module and provides smart GET,
PUT and POST endpoints classes.

>>> from dposlib import rest
>>> rest.use("ark")
>>> # = 'http://explorer.ark.io:8443/api/delegates/get?username=arky'
>>> rest.GET.api.delegates.get(username="arky")
{'success': True, 'delegate': {'vote': '142348239372385', 'producedblocks': 107\
856, 'productivity': 98.63, 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE', 'r\
ate': 42, 'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe\
110d60a15e9', 'approval': 1.05, 'username': 'arky', 'missedblocks': 1499}}

If you know the content key of blockchain response you can ask it using
`returnKey` keyword (satoshi values are converted to float values).
>>> rest.GET.api.delegates.get(username="arky", returnKey="delegate")
{'publicKey': '030da05984d579395ce276c0dd6ca0a60140a3c3d964423a04e7abe110d60a15\
e9', 'rate': 42, 'approval': 1.05, 'producedblocks': 107858, 'missedblocks': 14\
96, 'address': 'ARfDVWZ7Zwkox3ZXtMQQY1HYSANMB88vWE', 'vote': 1423484.39372385, \
'productivity': 98.63, 'username': 'arky'}

`rest` also creates a `core` module to `dposlib` package containing transactions
functions and `crypto` module. 

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

from importlib import import_module

import requests

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
	def _GET(*args, **kwargs):
		# API response contains several fields and wanted one can be extracted using
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
			# print(req.url)
			data = req.json()
		except Exception as error:
			data = {"success": False, "error": error, "peer": peer}
		else:
			if return_key in data:
				data = data.get(return_key, {})
				if isinstance(data, dict):
					data = filter_dic(data)
		return data

	@staticmethod
	def _POST(*args, **kwargs):
		peer = kwargs.pop("peer", False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			data = requests.post(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			).json()
		except Exception as error:
			data = {"success": False, "error": error, "peer": peer}
		return data

	@staticmethod
	def _PUT(*args, **kwargs):
		peer = kwargs.pop("peer", False)
		peer = peer if peer else random.choice(cfg.peers)
		try:
			data = requests.put(
				peer + "/".join(args),
				data=json.dumps(kwargs),
				headers=cfg.headers,
				verify=cfg.verify,
				timeout=cfg.timeout
			).json()
		except Exception as error:
			data = {"success": False, "error": error, "peer": peer}
		return data

	def __init__(self, elem=None, parent=None, method=None):
		if method not in [EndPoint._GET, EndPoint._POST, EndPoint._PUT]:
			raise Exception("REST method is not a valid one")
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


#######################
#  network selection  #
#######################

def load(family_name):
	"""
	Loads a given blockchain package as `dposlib.core`
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
	cfg.__dict__.clear()
	cfg.network = None
	cfg.hotmode = False
	
	path = os.path.join(ROOT, "network", network + ".net")
	if os.path.exists(path):
		with io.open(os.path.join(ROOT, "network", network + ".net")) as f:
			data = json.load(f)
	else:
		raise Exception('"{}" blockchain parameters does not exist'.format(network))
	data.update(**kwargs)

	cfg.__dict__.update(data)
	cfg.verify = os.path.join(os.path.dirname(sys.executable), 'cacert.pem') if FROZEN else True

	if data.get("seeds", False):
		cfg.peers = []
		for seed in cfg.seeds:
			if check_latency(seed):
				cfg.peers.append(seed)
				break
	else:
		for peer in data.get("peers", []):
			peer = "http://{0}:{1}".format(peer, data.get("port", 22))
			if check_latency(peer):
				cfg.peers = [peer]
				break

	if len(cfg.peers):
		load(cfg.familly)
		cfg.network = network
		cfg.hotmode = True
	else:
		raise Exception("Error occurred during network setting...")
